from src.core.states.guild_chest_storage import GuildChestStorage


def make_guild_chest_storage() -> GuildChestStorage:
    return GuildChestStorage.for_server(1)
