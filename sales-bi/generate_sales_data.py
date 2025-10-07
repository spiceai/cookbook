#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "duckdb",
#     "numpy",
#     "pandas",
# ]
# ///
from __future__ import annotations

import argparse
import calendar
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import duckdb
import numpy as np
import pandas as pd


@dataclass
class ReferenceData:
    products: pd.DataFrame
    product_codes: np.ndarray
    product_weights: np.ndarray
    customers: pd.DataFrame
    customer_names: np.ndarray
    customer_weights: np.ndarray
    status_choices: List[str]
    status_weights: np.ndarray
    quantity_choices: np.ndarray
    line_item_sizes: np.ndarray
    line_item_weights: np.ndarray
    month_choices: np.ndarray
    month_weights: np.ndarray
    deal_size_thresholds: Tuple[float, float]
    existing_max_order: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate realistic synthetic sales data based on an existing dataset."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("sales-bi/cleaned_sales_data.parquet"),
        help="Path to the seed parquet file used for profiling the existing data.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("sales-bi/cleaned_sales_data.parquet"),
        help="Destination parquet file for the generated data.",
    )
    parser.add_argument(
        "--num-orders",
        type=int,
        default=3500,
        help="Number of orders to generate (each order may have multiple line items).",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2021,
        help="Earliest year for synthesized order dates.",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=2023,
        help="Latest year for synthesized order dates.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible data generation.",
    )

    args = parser.parse_args()
    if args.num_orders <= 0:
        parser.error("--num-orders must be positive.")
    if args.start_year > args.end_year:
        parser.error("--start-year must be less than or equal to --end-year.")
    return args


def load_reference_df(path: Path) -> pd.DataFrame:
    escaped_path = str(path).replace("'", "''")
    with duckdb.connect(database=":memory:") as con:
        return con.execute(
            f"SELECT * FROM read_parquet('{escaped_path}')"
        ).fetch_df()


def normalize_weights(counts: Iterable[int]) -> np.ndarray:
    counts_arr = np.array(list(counts), dtype="float64")
    total = counts_arr.sum()
    if total == 0:
        raise ValueError("Cannot normalize zero weights.")
    return counts_arr / total


def compute_deal_size_thresholds(df: pd.DataFrame) -> Tuple[float, float]:
    small_sales = df.loc[df["deal_size"] == "Small", "sales"]
    medium_sales = df.loc[df["deal_size"] == "Medium", "sales"]
    small_cutoff = float(small_sales.quantile(0.95)) if not small_sales.empty else float(df["sales"].quantile(0.33))
    medium_cutoff = float(medium_sales.quantile(0.95)) if not medium_sales.empty else float(df["sales"].quantile(0.66))
    return small_cutoff, max(small_cutoff + 1.0, medium_cutoff)


def prepare_reference(df: pd.DataFrame) -> ReferenceData:
    product_counts = df.groupby("product_code").size()
    product_weights = normalize_weights(product_counts.values)
    product_stats = (
        df[["product_code", "product_line", "msrp"]]
        .drop_duplicates(subset="product_code")
        .set_index("product_code")
    )
    price_stats = df.groupby("product_code")["price_each"].agg(["mean", "std"])
    products = product_stats.join(price_stats).fillna({"std": 0.0})

    customer_counts = df.groupby("customer_name").size()
    customer_weights = normalize_weights(customer_counts.values)
    customers = (
        df[
            [
                "customer_name",
                "phone",
                "address_line1",
                "address_line2",
                "city",
                "state",
                "postal_code",
                "country",
                "territory",
                "contact_last_name",
                "contact_first_name",
            ]
        ]
        .drop_duplicates(subset="customer_name")
        .set_index("customer_name")
    )

    status_counts = df["status"].value_counts()
    status_choices = status_counts.index.tolist()
    status_weights = normalize_weights(status_counts.values)

    quantity_choices = df["quantity_ordered"].values

    line_items_per_order = df.groupby("order_number").size()
    line_item_freq = line_items_per_order.value_counts().sort_index()
    line_item_sizes = line_item_freq.index.to_numpy()
    line_item_weights = normalize_weights(line_item_freq.values)

    month_counts = df["month"].value_counts().sort_index()
    month_choices = month_counts.index.to_numpy()
    month_weights = normalize_weights(month_counts.values)

    deal_thresholds = compute_deal_size_thresholds(df)
    max_order = int(df["order_number"].max())

    return ReferenceData(
        products=products,
        product_codes=product_counts.index.to_numpy(),
        product_weights=product_weights,
        customers=customers,
        customer_names=customer_counts.index.to_numpy(),
        customer_weights=customer_weights,
        status_choices=status_choices,
        status_weights=status_weights,
        quantity_choices=quantity_choices,
        line_item_sizes=line_item_sizes,
        line_item_weights=line_item_weights,
        month_choices=month_choices,
        month_weights=month_weights,
        deal_size_thresholds=deal_thresholds,
        existing_max_order=max_order,
    )


def sample_price(row: pd.Series, rng: np.random.Generator) -> float:
    base_price = row["mean"]
    price_std = row["std"] if np.isfinite(row["std"]) else 0.0
    jitter = price_std if price_std > 0 else max(0.02 * base_price, 0.5)
    sampled = rng.normal(loc=base_price, scale=jitter)
    clipped = np.clip(sampled, row["msrp"] * 0.6, row["msrp"] * 1.25)
    return round(float(clipped), 2)


def choose_deal_size(sales: float, thresholds: Tuple[float, float]) -> str:
    small_cutoff, medium_cutoff = thresholds
    if sales <= small_cutoff:
        return "Small"
    if sales <= medium_cutoff:
        return "Medium"
    return "Large"


def synthesize_orders(
    ref: ReferenceData,
    num_orders: int,
    year_range: Tuple[int, int],
    rng: np.random.Generator,
) -> pd.DataFrame:
    records: List[Dict[str, object]] = []
    product_choices = ref.product_codes
    customer_choices = ref.customer_names

    for idx, order_number in enumerate(
        range(ref.existing_max_order + 1, ref.existing_max_order + 1 + num_orders), start=1
    ):
        num_items = int(rng.choice(ref.line_item_sizes, p=ref.line_item_weights))
        customer_name = rng.choice(customer_choices, p=ref.customer_weights)
        customer_row = ref.customers.loc[customer_name].where(pd.notnull, None)

        month = int(rng.choice(ref.month_choices, p=ref.month_weights))
        year = int(rng.integers(year_range[0], year_range[1] + 1))
        day = int(rng.integers(1, calendar.monthrange(year, month)[1] + 1))
        order_dt = datetime(year, month, day)
        quarter = (month - 1) // 3 + 1

        status = rng.choice(ref.status_choices, p=ref.status_weights)

        for line_idx in range(1, num_items + 1):
            product_code = rng.choice(product_choices, p=ref.product_weights)
            product_row = ref.products.loc[product_code]

            quantity = int(rng.choice(ref.quantity_choices))
            price_each = sample_price(product_row, rng)
            sales = round(quantity * price_each, 2)
            deal_size = choose_deal_size(sales, ref.deal_size_thresholds)

            records.append(
                {
                    "order_number": order_number,
                    "quantity_ordered": quantity,
                    "price_each": price_each,
                    "order_line_number": line_idx,
                    "sales": sales,
                    "order_date": order_dt,
                    "status": status,
                    "quarter": quarter,
                    "month": month,
                    "year": year,
                    "product_line": product_row["product_line"],
                    "msrp": int(product_row["msrp"]),
                    "product_code": product_code,
                    "customer_name": customer_name,
                    "phone": customer_row["phone"],
                    "address_line1": customer_row["address_line1"],
                    "address_line2": customer_row["address_line2"],
                    "city": customer_row["city"],
                    "state": customer_row["state"],
                    "postal_code": customer_row["postal_code"],
                    "country": customer_row["country"],
                    "territory": customer_row["territory"],
                    "contact_last_name": customer_row["contact_last_name"],
                    "contact_first_name": customer_row["contact_first_name"],
                    "deal_size": deal_size,
                }
            )

    df = pd.DataFrame.from_records(records)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df.sort_values(["order_number", "order_line_number"]).reset_index(drop=True)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(database=":memory:") as con:
        con.register("new_data", df)
        con.execute("COPY new_data TO ? (FORMAT 'parquet')", [str(path)])


def main() -> None:
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    reference_df = load_reference_df(args.input)
    reference = prepare_reference(reference_df)
    synthesized = synthesize_orders(
        reference,
        num_orders=args.num_orders,
        year_range=(args.start_year, args.end_year),
        rng=rng,
    )
    write_parquet(synthesized, args.output)

    line_items = len(synthesized)
    unique_orders = synthesized["order_number"].nunique()
    print(
        f"Wrote {line_items} line items across {unique_orders} orders to {args.output} "
        f"using years {args.start_year}-{args.end_year}."
    )


if __name__ == "__main__":
    main()
