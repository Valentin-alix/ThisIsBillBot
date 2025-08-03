/* global Module, NativeFunction, Interceptor, Memory, Process, send */

'use strict';

let retroCdnList = [];
let localProxyPort = 0;
let proxyIp = [127, 0, 0, 1];


recv(function (config) {
    if (Array.isArray(config.retroCdn)) {
        retroCdnList = config.retroCdn;
    }
    if (typeof config.port === 'number') {
        localProxyPort = config.port;
    }
    if (Array.isArray(config.proxyIp) && config.proxyIp.length === 4) {
        proxyIp = config.proxyIp;
    }
    hookConnect();
    send('hooks_ready');
});

function hookConnect() {
    try {
        const connectPtr = Module.getExportByName(null, 'connect');
        const sendPtr = Module.getExportByName(null, 'send');

        const socketSend = new NativeFunction(sendPtr, 'int', [
            'int',
            'pointer',
            'int',
            'int'
        ]);

        Interceptor.attach(connectPtr, {
            onEnter(args) {
                this.sockfd = args[0];
                const sockaddrPtr = args[1];

                const portHigh = sockaddrPtr.add(2).readU8();
                const portLow = sockaddrPtr.add(3).readU8();
                this.port = (portHigh << 8) + portLow;

                const octets = [];
                for (let i = 0; i < 4; i += 1) {
                    octets.push(sockaddrPtr.add(4 + i).readU8());
                }
                this.addr = octets.join('.');

                if (
                    retroCdnList.includes(this.addr) ||
                    this.addr === '127.0.0.1' ||
                    this.addr === '::1' ||
                    localProxyPort === 0
                ) {
                    this.shouldSend = false;
                    return;
                }

                const newPortHigh = (localProxyPort >> 8) & 0xff;
                const newPortLow = localProxyPort & 0xff;

                sockaddrPtr.add(2).writeByteArray([newPortHigh, newPortLow]);
                sockaddrPtr.add(4).writeByteArray(proxyIp);

                this.shouldSend = true;
            },

            onLeave() {
                if (!this.shouldSend) {
                    return;
                }

                const connectRequest =
                    `CONNECT ${this.addr}:${this.port} HTTP/1.0\r\n\r\n`;

                const buf = Memory.allocUtf8String(connectRequest);

                socketSend(
                    this.sockfd.toInt32(),
                    buf,
                    connectRequest.length,
                    0
                );
            }
        });

        const createProcessWPtr = Module.getExportByName(null, 'CreateProcessW');

        Interceptor.attach(createProcessWPtr, {
            onEnter(args) {
                this.pidStruct = null;

                const applicationName = args[0].isNull()
                    ? null
                    : Memory.readUtf16String(args[0]);

                const commandLine = args[1].isNull()
                    ? null
                    : Memory.readUtf16String(args[1]);

                if (!applicationName && commandLine) {
                    if (
                        commandLine.includes('network') ||
                        commandLine.includes('plugins')
                    ) {
                        this.pidStruct = args[9];
                    }
                }
            },

            onLeave() {
                if (!this.pidStruct) {
                    return;
                }

                const hProcess = this.pidStruct
                    .add(Process.pointerSize * 2)
                    .readInt();

                send(parseInt(hProcess, 10));
                this.pidStruct = null;
            }
        });
    } catch (err) {
        console.log(`ERREUR: ${err.message}`);
    }
}

