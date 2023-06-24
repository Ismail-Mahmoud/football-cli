from __future__ import annotations
import pydantic
from pydantic import BaseModel as PydanticBaseModel, root_validator
from typing import Optional
from datetime import datetime


class BaseModel(PydanticBaseModel):
    class Config:
        allow_mutation = False


class Area(BaseModel):
    id: int
    name: str
    code: Optional[str] = None
    flag: Optional[str] = None
    parentAreaId: Optional[int] = None
    parentArea: Optional[str] = None


class Competition(BaseModel):
    id: int
    name: str
    code: str
    type: str
    seasons: list[Season] = []

    @property
    def is_league(self):
        return self.type == "LEAGUE"


class Season(BaseModel):
    id: int
    startDate: str
    endDate: str
    year: Optional[str] = None
    winner: Optional[Team] = None
    currentMatchday: Optional[int] = None

    @root_validator
    def set_year(cls, values):
        start_year = values["startDate"].split('-')[0]
        end_year = values["endDate"].split('-')[0]
        values["year"] = start_year if start_year == end_year else f"{start_year}/{end_year}"

        return values


class CompetitionTeams(BaseModel):
    count: int
    competition: Competition
    season: Season
    teams: list[Team]


class Team(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    fullName: Optional[str] = None
    shortName: Optional[str] = None
    tla: Optional[str] = None
    area: Optional[Area] = None
    clubColors: Optional[str] = None
    venue: Optional[str] = None
    founded: Optional[int] = None
    coach: Optional[Person] = None
    squad: Optional[list[Person]] = None

    @root_validator
    def set_name(cls, values):
        values["fullName"] = values["name"]
        values["name"] = values["shortName"] or values["fullName"] or values["tla"] or values["id"]

        return values


class Standings(BaseModel):
    standings: list[Standing]
    competition: Competition


class Standing(BaseModel):
    type: str
    table: list[TableRecord]
    group: Optional[str] = None


class TableRecord(BaseModel):
    position: int
    team: Team
    playedGames: int
    won: int
    draw: int
    lost: int
    points: int
    goalsFor: int
    goalsAgainst: int
    goalDifference: int
    form: Optional[str] = None


class MatchesResultSet(BaseModel):
    count: Optional[int] = None
    competitions: Optional[str] = None
    first: Optional[str] = None
    last: Optional[str] = None
    played: Optional[int] = None
    wins: Optional[int] = None
    draws: Optional[int] = None
    losses: Optional[int] = None


class MatchSet(BaseModel):
    matches: list[Match]
    aggregates: Optional[Head2HeadAggregates] = None
    resultSet: Optional[MatchesResultSet] = None


class Match(BaseModel):
    id: int
    status: str
    utcDate: datetime
    homeTeam: Team
    awayTeam: Team
    score: MatchScore
    season: Season | str
    competition: Competition | str
    matchday: Optional[int | str] = None
    stage: Optional[str] = None
    group: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None

    @property
    def is_live(self):
        return self.status in ["LIVE", "IN_PLAY", "PAUSED"]

    @root_validator
    def set_match_atrributes(cls, values):
        if isinstance(values["competition"], Competition):
            values["competition"] = values["competition"].name

        if isinstance(values["season"], Season):
            values["season"] = values["season"].year

        if values["stage"] in [None, "REGULAR_SEASON", "Regular Season"]:   # League competition
            values["stage"] = None
            values["group"] = None

        if values["stage"] not in [None, "GROUP_STAGE"]:    # Cup competition elimination rounds
            values["matchday"] = None

        if values["matchday"] is not None:      # Format matchday
            values["matchday"] = f'Matchday_{str(values["matchday"]).zfill(2)}'

        values["date"] = values["utcDate"].strftime("%Y-%m-%d")
        values["time"] = "TBD" if values["status"] == "SCHEDULED" else values["utcDate"].strftime("%H:%M %Z")

        return values


class Score(BaseModel):
    home: Optional[int] = None
    away: Optional[int] = None


class MatchScore(BaseModel):
    fullTime: Score
    halfTime: Score
    regularTime: Optional[Score] = None
    extraTime: Optional[Score] = None
    penalties: Optional[Score] = None
    winner: Optional[str] = None
    duration: Optional[str] = None


class Person(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    dateOfBirth: Optional[str] = None
    nationality: Optional[str] = None
    shirtNumber: Optional[int] = None
    position: Optional[str] = None
    section: Optional[str] = None

    @root_validator
    def set_name(cls, values):
        if values["name"]:
            return values

        name = values["firstName"] or ""
        name += " " if values["firstName"] and values["lastName"] else ""
        name += values["lastName"] or ""
        values["name"] = name or None

        return values


class Head2HeadTeamAggregates(BaseModel):
    id: int
    name: str
    wins: int
    draws: int
    losses: int


class Head2HeadAggregates(BaseModel):
    numberOfMatches: int
    totalGoals: int
    homeTeam: Head2HeadTeamAggregates
    awayTeam: Head2HeadTeamAggregates


class Scorer(BaseModel):
    player: Person
    team: Team
    playedMatches: int
    goals: int
    assists: Optional[int] = None
    penalties: Optional[int] = None
    goals_per_match: Optional[int] = None

    @root_validator
    def set_to_zero(cls, values):
        values["assists"] = values["assists"] or 0
        values["penalties"] = values["penalties"] or 0

        return values


class TopScorers(BaseModel):
    scorers: list[Scorer]


def update_forward_refs():
    globals_ = globals().copy()
    for _, cls in globals_.items():
        if isinstance(cls, pydantic.main.ModelMetaclass):
            cls.update_forward_refs()
