from pydantic import BaseModel, Field
from typing import List, Optional


class Image(BaseModel):
    url: str
    description: str
    prompt: str


class PlotHook(BaseModel):
    title: str
    description: str = Field(description="HTML formatted description of the plot hook.")


class PlotStep(BaseModel):
    title: str
    description: str = Field(
        description="HTML formatted description of this plot step.", words=200
    )


class StatBlock(BaseModel):
    AC: int
    Initiative: int
    HP: int
    Speed: int
    Swim: int
    Str: int
    Dex: int
    Con: int
    Int: int
    Wis: int
    Cha: int
    CR: int
    XP: int
    PB: int


class Character(BaseModel):
    name: str
    image: Image
    stats: StatBlock
    role: str
    goal: str
    quirk: str
    description: str


class Monster(BaseModel):
    name: str
    image: Image
    stats: StatBlock
    Traits: str
    description: str


class Reward(BaseModel):
    name: str
    description: str = Field(description="HTML formatted description of the reward.")
    image: Image


class MagicItem(BaseModel):
    name: str
    image: Image
    description: str = Field(
        description="HTML formatted description of the magic item."
    )


class PlotTwist(BaseModel):
    title: str
    description: str = Field(
        description="HTML formatted description of the plot twist."
    )


class Campaign_Schema(BaseModel):
    title: str
    setting: str
    partySize: int
    characterLevel: int
    history: str
    atmosphere: str
    setup: str = Field(
        description="HTML formatted setup and background story for the module."
    )
    startingPointImage: Image
    mapImagePrompt: Image
    plotHooks: List[PlotHook]
    mainPlotSteps: List[PlotStep]
    mainCharacters: List[Character]
    monsters: List[Monster]
    rewardsImagePrompt: Image
    rewardsList: List[Reward]
    generatedMagicItems: List[MagicItem]
    generatedPlotTwists: List[PlotTwist]


class Campaign:
    json = {}
    images = []
    html = ""
