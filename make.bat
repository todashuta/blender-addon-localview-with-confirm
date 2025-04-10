@echo off

pushd %~dp0

if not defined BLENDER_USER_SCRIPTS (
	goto blender_user_scripts_not_defined
)

if not exist "%BLENDER_USER_SCRIPTS%\addons\" (
	goto addons_dir_not_exist
)

set NAME=localview_with_confirm.py

COPY ".\%NAME%" "%BLENDER_USER_SCRIPTS%\addons\%NAME%"
goto end

:blender_user_scripts_not_defined
echo BLENDER_USER_SCRIPTS not defined
goto end

:addons_dir_not_exist
echo addons directory does not exist
goto end

:end
pause
