@echo off
SETLOCAL
set SCRIPT_PATH=%~dp0
set LOCAL=%SCRIPT_PATH%\.local\.ddb
set PORT=8000

E:
IF NOT EXIST %LOCAL%  MKDIR %LOCAL%

CD /D %LOCAL%


START java -Djava.library.path=%DYNAMODB_PATH%\DynamoDBLocal_lib -jar  %DYNAMODB_PATH%\DynamoDBLocal.jar -port %PORT% -sharedDb

IF %ERRORLEVEL% NEQ 0 ( 
   echo Failed to Start DynamoDB server. (DYNAMODB_PATH=%DYNAMODB_PATH%)
) ELSE (
   echo Started DynamoDB server on http://localhost:%PORT%
)



ENDLOCAL
