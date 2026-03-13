const TARGET_PORTS = new Set([5555]);

recv(function (message) {
    const proxyPort = message.port;
    const proxyIp = Array.isArray(message.proxyIp) && message.proxyIp.length === 4
        ? message.proxyIp
        : [127, 0, 0, 1];
    hookConnect(proxyPort, proxyIp);
});


function hookConnect(proxyPort, proxyIp) {
    const connectPtr = Module.getExportByName("ws2_32.dll", "connect");

    Interceptor.attach(connectPtr, {
        onEnter(args) {
            try {
                const sockaddr = args[1];
                const family = sockaddr.readU16();

                // add(nb octet) permet de déplacer le point à nb d'octet apres sockaddr
                if (family === 2) { // IPV4
                    const port = (sockaddr.add(2).readU8() << 8) | sockaddr.add(3).readU8();

                    if (!TARGET_PORTS.has(port)) return

                    sockaddr.add(4).writeByteArray(proxyIp);
                    sockaddr.add(2).writeU8((proxyPort >> 8) & 0xFF);
                    sockaddr.add(3).writeU8(proxyPort & 0xFF);

                } else if (family === 23) { // IPV6
                    const port =
                        (sockaddr.add(2).readU8() << 8) |
                        sockaddr.add(3).readU8();

                    if (!TARGET_PORTS.has(port)) return;

                    const ipv6 = sockaddr.add(8);

                    ipv6.writeByteArray([
                        0x00, 0x00, 0x00, 0x00, // 0-3
                        0x00, 0x00, 0x00, 0x00, // 4-7
                        0x00, 0x00, 0xFF, 0xFF, // 8-11
                        proxyIp[0], proxyIp[1], proxyIp[2], proxyIp[3]
                    ]);

                    sockaddr.add(2).writeU8((proxyPort >> 8) & 0xFF);
                    sockaddr.add(3).writeU8(proxyPort & 0xFF);
                }
            }
            catch (err) {
                console.info(err.message)
            }
        }
    });
}
