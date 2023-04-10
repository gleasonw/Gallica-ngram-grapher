from io import StringIO
from www.models import Ticket
import aiohttp
from gallicaGetter.utils.date import Date
from gallicaGetter.periodOccurrence import PeriodRecord
from typing import Callable, Literal
from urllib.error import HTTPError
import pandas as pd
from urllib.parse import quote


async def get(args: Ticket, on_no_records_found: Callable):
    """Get records from Pyllica. Interpret 500 error as no records found."""
    print(args.link_term)
    if len(args.terms) > 1:
        raise ValueError("Only one term at a time for Pyllica, for now")
    if args.start_date is None:
        debut = 1789
    else:
        debut = int(Date(args.start_date).year)
    if args.end_date is None:
        fin = 1950
    else:
        fin = int(Date(args.end_date).year)
    try:
        if args.link_term:
            periods = await get_contain_data(
                mot1=args.terms[0],
                mot2=args.link_term,
                corpus=args.source,
                resolution="mois",
                debut=debut,
                fin=fin,
            )
        else:
            periods = await get_gram_data(
                gram=args.terms[0],
                corpus=args.source,
                resolution="mois",
                debut=debut,
                fin=fin,
            )
    except HTTPError:
        on_no_records_found()
        return
    if all(periods.ratio == 0):
        on_no_records_found()
        return
    return convert_data_frame_to_grouped_record(periods)


def convert_data_frame_to_grouped_record(frame):
    if "mois" not in frame.columns:
        dates = frame.annee
    else:
        dates = frame.apply(lambda row: f"{row.annee}-{row.mois:02}", axis=1)
    return (
        PeriodRecord(
            _date=Date(date),
            count=count,
            term=term,
        )
        for date, count, term in zip(dates, frame.ratio, frame.gram)
    )


async def get_contain_data(
    mot1: str,
    mot2: str,
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
    debut=1789,
    fin=1950,
    resolution: Literal["default", "annee", "mois"] = "default",
):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://shiny.ens-paris-saclay.fr/guni/contain",
            params={
                "corpus": corpus,
                "mot1": mot1.lower(),
                "mot2": mot2.lower(),
                "from": debut,
                "to": fin,
            },
        ) as response:
            return await parse_df(
                response=response, resolution=resolution, corpus=corpus
            )


async def get_gram_data(
    gram: str,
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
    debut=1789,
    fin=1950,
    resolution: Literal["default", "annee", "mois"] = "default",
):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://shiny.ens-paris-saclay.fr/guni/query",
            params={
                "corpus": corpus,
                "mot": gram.lower(),
                "from": debut,
                "to": fin,
            },
        ) as response:
            return await parse_df(
                response=response, resolution=resolution, corpus=corpus
            )


async def parse_df(
    response: aiohttp.ClientResponse,
    resolution: Literal["default", "annee", "mois"] = "default",
    corpus: Literal["lemonde", "livres", "presse"] = "presse",
):
    df = pd.read_csv(StringIO(await response.text()))
    if resolution == "mois" and corpus != "livres":
        df = (
            df.groupby(["annee", "mois", "gram"])
            .agg({"n": "sum", "total": "sum"})
            .reset_index()
        )
    if resolution == "annee":
        df = (
            df.groupby(["annee", "gram"])
            .agg({"n": "sum", "total": "sum"})
            .reset_index()
        )

    def calc_ratio(row):
        if row.total == 0:
            return 0
        return row.n / row.total

    df["ratio"] = df.apply(lambda row: calc_ratio(row), axis=1)
    return df
