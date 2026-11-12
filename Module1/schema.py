from pydantic import BaseModel, Field
class TextRequest(BaseModel):
  topic: str = Field(..., description="The topic for which the text is requested.", example = "Neural networks")
  course: str = Field(..., description="The course for which the text is requested.", example = "Artificial Intelligence")
  student_level: str = Field(..., description="The educational level of the student.", example = "Beginner")
  
  