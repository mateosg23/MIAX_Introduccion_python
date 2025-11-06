from run_manual import run
from run_auto import run_auto

def main():
    """
    Método que permite al usuario elegir la versión automatizada del programa o la no automatizada
    """

    print("====================================================")
    print("     SIMULADOR DE MONTE CARLO DE CARTERA FINANCIERA")
    print("====================================================\n")

    opcion = input('¿Quieres usar la versión automatizada del proceso de simulación? (S/N): ').upper()
    if opcion=='S':
        run_auto()
    elif opcion == 'N':
        run()
    else:
        raise ValueError('Introduce una opción permitida (S/N)')
    
# Ejecutamos el programa
if __name__ == "__main__":
    main()