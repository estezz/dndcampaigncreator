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
    description: str = Field(description="HTML formatted description of this plot step.", words=200)

class Character(BaseModel):
    name: str
    image: Image
    role: str
    description: str = Field(description="HTML formatted description of the character.")    

class Monster(BaseModel):
    name: str
    statBlock: str = Field(description="HTML formatted stat block for the monster.")

class Reward(BaseModel):
    name: str
    description: str = Field(description="HTML formatted description of the reward.")

class MagicItem(BaseModel):
    name: str
    image: Image
    description: str = Field(description="HTML formatted description of the magic item.")

class PlotTwist(BaseModel):
    title: str
    description: str = Field(description="HTML formatted description of the plot twist.")


class Campaign_Schema(BaseModel):
    title: str
    setting: str
    partySize: int
    characterLevel: int
    history:str
    atmosphere: str
    setup: str = Field(description="HTML formatted setup and background story for the module.")
    startingPointImage: Image
    mapImagePrompt: Image
    plotHooks: List[PlotHook]
    mainPlotSteps: List[PlotStep]
    mainCharacters: List[Character]
    monsterStatBlocks: List[Monster]
    rewardsImagePrompt: Image
    rewardsList: List[Reward]
    generatedMagicItems: List[MagicItem]
    generatedPlotTwists: List[PlotTwist]

class Campaign():
    json = {}
    images = []
    html = ""