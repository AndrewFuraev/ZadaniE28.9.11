from pydantic import BaseModel, Field

class BookingDates(BaseModel):
    checkin: str
    checkout: str

class BookingResponseModel(BaseModel):
    firstname: str = Field(..., description="Имя клиента совершившего бронирование")
    lastname: str = Field(..., description="Фамилия клиента совершившего бронирование")
    totalprice: int = Field(..., description="Полная сумма бронирования")
    depositpaid: bool = Field(..., description="Был или не был уплачен задаток")
    bookingdates: dict = Field(..., description="Даты заезда и выезда")
    additionalneeds: str = Field(None, description="Пожелания гостя")

    class Config:
        allow_population_by_field_name = True


class CreateBookingRequest(BaseModel):
    firstname: str = Field(..., description="Имя клиента совершившего бронирование")
    lastname: str = Field(..., description="Фамилия клиента совершившего бронирование")
    totalprice: int = Field(..., description="Полная сумма бронирования")
    depositpaid: bool = Field(..., description="Был или не был уплачен задаток")
    bookingdates: BookingDates = Field(..., description="Даты заезда и выезда")
    additionalneeds: str = Field(..., description="Пожелания гостя")

class BookingResponse(BaseModel):
    bookingid: int
    booking: CreateBookingRequest


class Booking(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str

class CreateBookingResponse(BaseModel):
    bookingid: int