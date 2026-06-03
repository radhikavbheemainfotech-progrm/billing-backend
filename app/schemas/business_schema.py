# from pydantic import BaseModel
# from typing import Optional

# class BusinessProfileUdate(BaseModel):
#     business_name : Optional[str] = None
#     address : Optional[str] = None
#     phone : Optional[str] = None
#     email : Optional[str] = None
#     gst_number : Optional[str] = None
#     gst_percentage: Optional[float] = None
#     logo_url: Optional[str] = None


# class BusinessProfileOut(BaseModel):
#     id: int
#     business_name: str
#     address: Optional[str] = None
#     phone: Optional[str] = None
#     email : Optional[str] = None
#     gst_number : Optional[str] = None
#     gst_percentage : float
#     logo_url : Optional[str] = None

#     class Config:
#         from_attributes = True