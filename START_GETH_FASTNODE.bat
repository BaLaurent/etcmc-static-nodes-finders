@echo off
setlocal enabledelayedexpansion

title Ethereum Classic Node

:: Display the modification text
REM ------------------------------
REM Modifications by ETC Echo:
REM - Added bootnodes functionality for improved network connectivity
REM ------------------------------

set CONFIG_PATH=TESTPATH\config.toml

if not exist "!CONFIG_PATH!" (
	echo Configuration file not found at !CONFIG_PATH!.
	echo Please make sure the file exists and try again.
	pause
	exit /b
)
:: Start the Ethereum Classic Geth node with the specified configurations
geth --classic ^
--config "!CONFIG_PATH!" ^
--cache 1024 ^
--metrics ^
--identity "ETCMCgethNode" ^
console