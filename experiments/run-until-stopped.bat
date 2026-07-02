:: Define a marker named "loop" to serve as the jump destination
:loop

:: Execute the command for the experiment
acquire -c ghz -q 3 -m qpu

:: Pause execution for 1 second; /nobreak ensures only Ctrl+C can skip the wait
timeout /t 1 /nobreak

:: Instruct the script to jump back up to the ":loop" marker, running indefinitely
goto loop