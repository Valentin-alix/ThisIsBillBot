import json
from time import perf_counter
from typing import cast

import pandas as pd
import psycopg2
from pandas.core.indexes.accessors import TimedeltaProperties

from D3Database.data_center.data_reader import DataReader
from src.controller.scraping_d3_api.scraping_d3_client.scraping_d3_client.models.quantity_enum import (
    QuantityIndex,
)
from src.controller.speed_sell_score import SPEED_SCORE_BY_GID_PATH


def get_price_df():
    conn_params = {
        "host": "localhost",
        "port": 5432,
        "database": "postgres",
        "user": "postgres",
        "password": "postgres",
    }
    with psycopg2.connect(**conn_params) as conn:
        table_name = "item_price_history"
        query = f"SELECT * FROM {table_name};"
        df = pd.read_sql_query(query, conn)

    return df


def get_speed_sell_score(df: pd.DataFrame, gids: set[int]) -> dict[int, float]:
    quantity_map = {
        QuantityIndex.ONE.name: 1,
        QuantityIndex.TEN.name: 10,
        QuantityIndex.HUNDRED.name: 100,
        QuantityIndex.THOUSAND.name: 1000,
    }

    df = df[df["gid"].isin(gids)]

    df = df.dropna(subset=["price"])

    df["quantity_num"] = df["quantity"].map(quantity_map)

    df = df.sort_values(by=["gid", "quantity", "recorded_at"])
    # ici on ajoute une colonne prev_price qui correspond au prix précédent
    df["prev_price"] = df.groupby(["gid", "quantity"])["price"].shift(1)
    df["prev_time"] = df.groupby(["gid", "quantity"])["recorded_at"].shift(1)

    df = df.dropna(subset=["prev_price", "prev_time"])

    df["delta_time"] = (
        cast(
            TimedeltaProperties, (df["recorded_at"] - df["prev_time"]).dt
        ).total_seconds()
        / 3600
    )
    df["time_weight"] = 1 / (1 + df["delta_time"])
    df["is_buy"] = (df["price"] > df["prev_price"]).astype(int)
    df["sell_score"] = df["is_buy"] * df["quantity_num"] * df["time_weight"]

    item_speed = df.groupby("gid")["sell_score"].mean()
    return item_speed.to_dict()  # type: ignore


if __name__ == "__main__":
    before = perf_counter()

    print(len(set(DataReader().item_by_id)))

    speed_score_by_gid = get_speed_sell_score(
        get_price_df(), set(DataReader().item_by_id)
    )
    # for gid, speed in get_speed_sell_score(get_price_df(), GATHERER_ITEM_GIDS).items():
    #     print(I18N().name_by_id[DataReader().item_by_id[gid].nameId or 0], speed)

    with open(SPEED_SCORE_BY_GID_PATH, "w+") as file:
        json.dump(speed_score_by_gid, file)
