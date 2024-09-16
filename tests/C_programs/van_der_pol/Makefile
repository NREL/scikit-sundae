SUNDIALS_DIR = C:\Users\crandall\AppData\Anaconda\envs\sun\Library

CC = cl
CFLAGS = /MD /I"$(SUNDIALS_DIR)\include"
LDFLAGS = /link /LIBPATH:"$(SUNDIALS_DIR)\lib" \
		  		sundials_core.lib sundials_cvode.lib sundials_nvecserial.lib \
				sundials_sunlinsoldense.lib sundials_sunmatrixdense.lib

EXE = main.exe
OBJ = main.obj

run: $(EXE)
	@set PATH=$(SUNDIALS_DIR)/bin;%PATH%
	@$(EXE)

$(EXE): $(OBJ)
	$(CC) $(OBJ) $(LDFLAGS)

$(OBJ): main.c
	$(CC) /c main.c $(CFLAGS)

clean:
	del $(OBJ) $(EXE)
