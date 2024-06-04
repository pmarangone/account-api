from typing import Any, Dict

import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


def bad_request(body: Dict[str, Any]):
    return JSONResponse(
        content=jsonable_encoder(body),
        status_code=fastapi.status.HTTP_400_BAD_REQUEST,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    )


def not_found(body):
    return JSONResponse(
        content=jsonable_encoder(body),
        status_code=fastapi.status.HTTP_404_NOT_FOUND,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    )


def created(body):
    return JSONResponse(
        content=jsonable_encoder(body),
        status_code=fastapi.status.HTTP_201_CREATED,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    )


def success(body):

    return JSONResponse(
        content=jsonable_encoder(body),
        status_code=fastapi.status.HTTP_200_OK,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    )


def OK():
    return JSONResponse(
        content=jsonable_encoder("OK"),
        status_code=fastapi.status.HTTP_200_OK,
        headers={
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    )
