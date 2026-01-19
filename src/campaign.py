"""This module holds the state of the curently generated DnD Campaign"""

from typing import List
from pydantic import BaseModel, Field


class Image(BaseModel):
    """This class holds the state of an image"""

    url: str
    description: str
    prompt: str


class PlotHook(BaseModel):
    """This class represents the state of a Plot Hook"""

    title: str
    description: str = Field(description="HTML formatted description of the plot hook.")


class PlotStep(BaseModel):
    """This class holds the state of a Plot Step"""

    title: str
    description: str = Field(
        description="HTML formatted description of this plot step.", words=200
    )


class StatBlock(BaseModel):
    """This class holds the state of the states of a NPC or Monster"""

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
    """This class represents the traits  of a character"""

    name: str
    image: Image
    stats: StatBlock
    role: str
    goal: str
    quirk: str
    description: str


class Monster(BaseModel):
    """This class holds the traits of a Monster"""

    name: str
    image: Image
    stats: StatBlock
    Traits: str
    description: str


class Reward(BaseModel):
    """This class represents the state of a Reward"""

    name: str
    description: str = Field(description="HTML formatted description of the reward.")
    image: Image


class MagicItem(BaseModel):
    """This class represents a Magic Item"""

    name: str
    image: Image
    description: str = Field(
        description="HTML formatted description of the magic item."
    )


class PlotTwist(BaseModel):
    """This class holds the state of a Plot Twist"""

    title: str
    description: str = Field(
        description="HTML formatted description of the plot twist."
    )


class CampaignSchema(BaseModel):
    """This class brings together other state classes to form a full campaign as JSON Schema"""

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
    """This class brings togther the JSON, Images, and HTML that represents this Dnd Campaign"""

    json = {}
    images = []
    html = ""
