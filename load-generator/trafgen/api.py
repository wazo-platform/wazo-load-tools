#!/usr/bin/env python3

from fastapi import FastAPI, status, HTTPException
from fastapi.openapi.models import Response
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from invoke import run
from typing import Optional
from pydantic import BaseModel

class Command(BaseModel):
    cmd: str

    

@app.get("/status")
async def status():
    return {}

@app.post("/shell/")
async def shell(cmd: Command):
    cmd_dict = cmd.dict()
    command = cmd_dict.get("cmd")
    result = run(command, hide=True, warn=True)
    if result.ok:
        print(command)
    if result.ok:
        headers = {"Accept-Encoding": "gzip", "Content-Encoding": "gzip"}
        content = {"output": f"{result.stdout}"}
        return JSONResponse(content=content, headers=headers)
    else:
        raise HTTPException(
            status_code=500,
            detail=f'{result.stderr}',
        )
    


@app.exception_handler(422)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.errors()}
    )