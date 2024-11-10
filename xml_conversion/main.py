import base64
import logging
import secrets
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from xml_conversion.settings import settings
from xml_conversion.xml_utils import convert_rossum_content

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()
security = HTTPBasic()


def authorization(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    given_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = settings.username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        given_username_bytes, correct_username_bytes
    )
    given_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = settings.password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        given_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


def success(success: bool):
    return {"success": success}


@app.get("/export")
async def export(
    queue_id: int,
    annotation_id: int,
    authorized: Annotated[bool, Depends(authorization)],
):
    if not authorized:
        logger.critical("`authorized` is set to False. Something is terribly wrong!")
        return success(False)

    # request Rossum API
    headers = {"Authorization": settings.rossum_api_token}
    url = settings.rossum_api_url_template.format(
        queue_id=queue_id, annotation_id=annotation_id
    )

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != httpx.codes.OK:  # TODO: suggest retry
        logger.info(
            "Rossum API request failed: status code=%s; queue_id=%s; annotation_id=%s",
            response.status_code,
            queue_id,
            annotation_id,
        )
        return success(False)

    rossum_content = response.text

    # reformat the content
    simplified_content = convert_rossum_content(rossum_content)

    payload = {
        "annotationId": annotation_id,
        "content": base64.b64encode(bytes(simplified_content, "utf-8")).decode("utf-8"),
    }

    # post to postbin
    async with httpx.AsyncClient() as client:
        response = await client.post(settings.postbin_url, json=payload)

    if response.status_code != httpx.codes.OK:
        logger.info(
            "Postbin request failed: status code=%s; queue_id=%s; annotation_id=%s",
            response.status_code,
            queue_id,
            annotation_id,
        )
        return success(False)

    return success(True)
