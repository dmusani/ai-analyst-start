"""Profile a CSV: shape, types, nulls, ids, date ranges and small value sets."""

import json
import sys
from pathlib import Path

import pandas as pd

# Columns with this many distinct values or fewer get their full value counts listed.
LOW_CARDINALITY_MAX = 20


def is_date_column(name: str) -> bool:
    """Return True if the column name follows Beam's date naming (`date`, `*_date`, `*_at`)."""
    return name == "date" or name.endswith("_date") or name.endswith("_at")


def profile_csv(path: str | Path) -> dict:
    """Return a profile of one CSV: shape, types, nulls, ids, date ranges and small value sets.

    Use it when meeting a table for the first time, before any analysis.
    """
    path = Path(path)
    # Read the header first and pick date columns by their name suffix. Beam's
    # exports name dates consistently, and guessing from values is slow and error prone.
    header = pd.read_csv(path, nrows=0).columns
    date_cols = [c for c in header if is_date_column(c)]
    df = pd.read_csv(path, parse_dates=date_cols)

    columns = [
        {
            "name": col,
            "dtype": str(df[col].dtype),
            "null_rate": round(float(df[col].isna().mean()), 4),
            "distinct": int(df[col].nunique()),
        }
        for col in df.columns
    ]

    # Take the first *_id column as the table's key; duplicates there mean the
    # table is not one row per id.
    id_column = next((c for c in df.columns if c.endswith("_id")), None)
    duplicate_ids = int(df[id_column].duplicated().sum()) if id_column else 0

    date_columns = []
    for col in date_cols:
        values = df[col].dropna()
        date_columns.append({
            "name": col,
            "min": values.min().isoformat() if len(values) else None,
            "max": values.max().isoformat() if len(values) else None,
        })

    low_cardinality = {}
    for col in df.columns:
        if col in date_cols or df[col].nunique() > LOW_CARDINALITY_MAX:
            continue
        # value_counts leaves nulls out; the null rate is already in the columns table.
        counts = df[col].value_counts()
        low_cardinality[col] = {str(k): int(v) for k, v in counts.items()}

    if id_column is None:
        grain_guess = None
    elif duplicate_ids == 0:
        grain_guess = f"one row per {id_column}"
    else:
        grain_guess = f"not one row per {id_column}; check the grain"

    return {
        "table": path.stem,
        "rows": len(df),
        "columns": columns,
        "id_column": id_column,
        "duplicate_ids": duplicate_ids,
        "date_columns": date_columns,
        "low_cardinality": low_cardinality,
        "grain_guess": grain_guess,
    }


def profile_to_yaml(result: dict) -> str:
    """Return a profile from profile_csv as a YAML note, ready for knowledge/beam/<table>.yaml.

    Generated keys (rows, columns, date_ranges, low_cardinality) come from the data.
    Keys a person or the profile skill fills in (meaning, open_questions, verdict)
    are left empty.
    """
    import yaml

    grain = result["grain_guess"]
    note = {
        "table": result["table"],
        "rows": result["rows"],
        "grain": {
            "statement": grain or "no id column found",
            "status": "guess",
        },
        "primary_key": result["id_column"],
        "columns": [
            {
                "name": col["name"],
                "dtype": col["dtype"],
                "null_rate": round(col["null_rate"], 4),
                "distinct": col["distinct"],
                "meaning": None,
                "meaning_status": "inferred",
            }
            for col in result["columns"]
        ],
        "date_ranges": [
            {"column": c["name"], "min": str(c["min"]), "max": str(c["max"])}
            for c in result["date_columns"]
        ],
        "low_cardinality": {
            name: {str(k): v for k, v in counts.items()}
            for name, counts in result["low_cardinality"].items()
        },
        "facts": [],
        "open_questions": [],
        "verdict": {"status": None, "reasons": []},
    }
    return yaml.safe_dump(note, sort_keys=False, allow_unicode=True, width=100)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python helpers/profile.py <path-to-csv>")
    print(json.dumps(profile_csv(sys.argv[1]), indent=2, default=str))
