#coding=utf-8
import uvicorn as u
import time
from fastapi import FastAPI,Depends,Request
from coronavirus import application
from tutorial import app03,app04,app05,app06,app07,app08
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# from fastapi.exceptions import RequestValidationError #请求错误处理
# from fastapi.responses import PlainTextResponse #响应错误处理
# from fastapi.exceptions import HTTPException #异常错误处理
# from starlette.exceptions import HTTPException as StarletteHTTPException
app =FastAPI(
    title='FastAPI Tutorial and API Docs',
    description='FastAPI教程 接口文档',
    version='1.0.0',
    docs_url='/docs',
    # dependencies=[Depends(verify_token),Depends(verify_key)],
    redoc_url='/redocs'
)

#mount表示将某个目录下一个完全独立的应用挂载过来，这个不会在API交互文档显示
# app.mount(path='/coronavirus/static', app=StaticFiles(directory='./coronavirus/static'),name='static')
app.mount(path='/static', app=StaticFiles(directory='./coronavirus/static'), name='static')

# @app.exception_handler(StarletteHTTPException)#重写HTTPEception异常处理器
# async def http_exception_handler(request,exc):
#     return PlainTextResponse(str(exc.detail),status_code=exc.status_code)

# @app.exception_handler(RequestValidationError)#重写亲请求验证的异常处理器
# async def validation_exception_handler(request,exc):
#     return PlainTextResponse(str(exc),status_code=400)

@app.middleware('http')
async def add_process_time_header(request:Request,call_next):#call_next 将request请求做为参数
    '''中间件'''
    start_time = time.time()
    response = await call_next(request)
    processtime = time.time() - start_time
    response.headers['X-Process-Time'] = str(processtime)
    return response

#实现跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1",
        "http://127.0.0.1:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(app03,prefix='/chapter03',tags=['第三章 请求参数和验证'])
app.include_router(app04,prefix='/chapter04',tags=['响应模型示例'])
app.include_router(app05,prefix='/chapter05',tags=['第五章 FastAPI的依赖注入系统'])
app.include_router(app06,prefix='/chapter06',tags=['第六章 安全、认证和授权'])
app.include_router(app07,prefix='/chapter07',tags=["第七章 FastAPI的数据库操作和多应用的目录结构设计"])
app.include_router(application,prefix='/coronavirus',tags=["第七章 FastAPI的数据库操作和多应用的目录结构设计"])
app.include_router(app08,prefix='/chapter08',tags=["中间件，后台任务，测试用例"])

if __name__ == '__main__':
    u.run('run:app',host='0.0.0.0',port=8081,reload=True,debug=True,workers=1)