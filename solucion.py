import copy

class Nodo:
    """Representa un nodo en el Árbol de Sintaxis Abstracta (AST)."""
    def __init__(self, valor, izquierdo=None, derecho=None):
        self.valor = valor
        self.izquierdo = izquierdo
        self.derecho = derecho

    def __repr__(self):
        return f"Nodo(valor='{self.valor}')"

def construir_ast_desde_expresion(expresion: str) -> Nodo:
    """
    Construye un Árbol de Sintaxis Abstracta a partir de una expresión lógica.
    Este parser respeta la precedencia de operadores y el uso de paréntesis.
    """
    expresion = expresion.strip()

    # Elimina paréntesis externos que envuelven toda la expresión.
    if expresion.startswith('(') and expresion.endswith(')'):
        nivel_parentesis = 0
        es_envoltorio_completo = True
        for char in expresion[1:-1]:
            if char == '(':
                nivel_parentesis += 1
            elif char == ')':
                nivel_parentesis -= 1
            if nivel_parentesis < 0:
                es_envoltorio_completo = False
                break
        if es_envoltorio_completo:
            return construir_ast_desde_expresion(expresion[1:-1])

    # Búsqueda de operadores por precedencia (de menor a mayor).
    operadores_por_precedencia = [['<->'], ['->'], ['v'], ['&']]
    for grupo_ops in operadores_por_precedencia:
        nivel_parentesis = 0
        for i in range(len(expresion) - 1, -1, -1):
            char = expresion[i]
            if char == ')':
                nivel_parentesis += 1
            elif char == '(':
                nivel_parentesis -= 1
            
            if nivel_parentesis == 0:
                for op in grupo_ops:
                    if expresion.startswith(op, i):
                        return Nodo(
                            valor=op,
                            izquierdo=construir_ast_desde_expresion(expresion[:i]),
                            derecho=construir_ast_desde_expresion(expresion[i + len(op):])
                        )

    # Manejo del operador unario de negación.
    if expresion.startswith('-'):
        return Nodo(valor='-', derecho=construir_ast_desde_expresion(expresion[1:]))
    
    # Caso base: el nodo es un operando (una variable proposicional).
    return Nodo(expresion)

def ast_a_cadena(nodo: Nodo) -> str:
    """Convierte un AST de vuelta a su representación en cadena."""
    if nodo is None:
        return ""
    if nodo.izquierdo is None and nodo.derecho is None:
        return nodo.valor
    
    str_izq = ast_a_cadena(nodo.izquierdo)
    str_der = ast_a_cadena(nodo.derecho)
    
    if nodo.valor == '-':
        return f"-({str_der})"
        
    return f"({str_izq} {nodo.valor} {str_der})"

# --- Implementación del Método Clásico ---

def eliminar_bicondicionales(nodo: Nodo) -> Nodo:
    """Paso 1: Reemplaza 'A <-> B' por '(A -> B) & (B -> A)'."""
    if nodo is None: return None
    nodo.izquierdo = eliminar_bicondicionales(nodo.izquierdo)
    nodo.derecho = eliminar_bicondicionales(nodo.derecho)
    
    if nodo.valor == '<->':
        p, q = nodo.izquierdo, nodo.derecho
        implicacion1 = Nodo('->', p, q)
        implicacion2 = Nodo('->', q, p)
        return Nodo('&', implicacion1, implicacion2)
    return nodo

def eliminar_implicaciones(nodo: Nodo) -> Nodo:
    """Paso 2: Reemplaza 'A -> B' por '-A v B'."""
    if nodo is None: return None
    nodo.izquierdo = eliminar_implicaciones(nodo.izquierdo)
    nodo.derecho = eliminar_implicaciones(nodo.derecho)

    if nodo.valor == '->':
        p, q = nodo.izquierdo, nodo.derecho
        negacion_p = Nodo('-', derecho=p)
        return Nodo('v', negacion_p, q)
    return nodo

def adentrar_negaciones_demorgan(nodo: Nodo) -> Nodo:
    """Paso 3: Aplica Leyes de De Morgan y elimina dobles negaciones."""
    if nodo is None: return None

    if nodo.valor == '-':
        hijo = nodo.derecho
        if hijo.valor == '-': # Doble negación: --A => A
            return adentrar_negaciones_demorgan(hijo.derecho)
        if hijo.valor == '&': # De Morgan: -(A & B) => -A v -B
            nuevo_izq = adentrar_negaciones_demorgan(Nodo('-', derecho=hijo.izquierdo))
            nuevo_der = adentrar_negaciones_demorgan(Nodo('-', derecho=hijo.derecho))
            return Nodo('v', nuevo_izq, nuevo_der)
        if hijo.valor == 'v': # De Morgan: -(A v B) => -A & -B
            nuevo_izq = adentrar_negaciones_demorgan(Nodo('-', derecho=hijo.izquierdo))
            nuevo_der = adentrar_negaciones_demorgan(Nodo('-', derecho=hijo.derecho))
            return Nodo('&', nuevo_izq, nuevo_der)
            
    nodo.izquierdo = adentrar_negaciones_demorgan(nodo.izquierdo)
    nodo.derecho = adentrar_negaciones_demorgan(nodo.derecho)
    return nodo

def distribuir_disyuncion_sobre_conjuncion(nodo: Nodo) -> Nodo:
    """Paso 4: Aplica la ley distributiva A v (B & C) => (A v B) & (A v C)."""
    if nodo is None: return None
    nodo.izquierdo = distribuir_disyuncion_sobre_conjuncion(nodo.izquierdo)
    nodo.derecho = distribuir_disyuncion_sobre_conjuncion(nodo.derecho)

    if nodo.valor == 'v':
        izq, der = nodo.izquierdo, nodo.derecho
        if der.valor == '&': # A v (B & C)
            b, c = der.izquierdo, der.derecho
            nuevo_izq = distribuir_disyuncion_sobre_conjuncion(Nodo('v', izq, b))
            nuevo_der = distribuir_disyuncion_sobre_conjuncion(Nodo('v', izq, c))
            return Nodo('&', nuevo_izq, nuevo_der)
        if izq.valor == '&': # (A & B) v C
            a, b = izq.izquierdo, izq.derecho
            nuevo_izq = distribuir_disyuncion_sobre_conjuncion(Nodo('v', a, der))
            nuevo_der = distribuir_disyuncion_sobre_conjuncion(Nodo('v', b, der))
            return Nodo('&', nuevo_izq, nuevo_der)
    return nodo

def convertir_a_fnc_clasico(nodo_raiz: Nodo) -> Nodo:
    """Ejecuta todos los pasos para la conversión clásica a FNC."""
    ast = eliminar_bicondicionales(nodo_raiz)
    ast = eliminar_implicaciones(ast)
    ast = adentrar_negaciones_demorgan(ast)
    # La distribución puede necesitar varias pasadas
    for _ in range(5): # Un número razonable de iteraciones para estabilizar
        ast = distribuir_disyuncion_sobre_conjuncion(ast)
    return ast

# --- Implementación del Método de Tseitin ---

class TransformadorTseitin:
    """
    Aplica la transformación de Tseitin para convertir una fórmula lógica
    en una FNC equisatisfacible de forma lineal.
    """
    def __init__(self):
        self.clausulas = []
        self.contador_var = 0
        self.mapa_subformula_a_var = {}

    def _nueva_variable(self):
        self.contador_var += 1
        return f"x{self.contador_var}"

    def transformar(self, nodo: Nodo) -> str:
        """Recorre el AST y genera las cláusulas de Tseitin."""
        cadena_nodo = ast_a_cadena(nodo)
        if cadena_nodo in self.mapa_subformula_a_var:
            return self.mapa_subformula_a_var[cadena_nodo]

        if nodo.izquierdo is None and nodo.derecho is None:
            return nodo.valor

        var_actual = self._nueva_variable()
        self.mapa_subformula_a_var[cadena_nodo] = var_actual
        
        var_der = self.transformar(nodo.derecho)
        var_izq = self.transformar(nodo.izquierdo) if nodo.izquierdo else None

        op = nodo.valor
        if op == '&':   # x <-> (a & b)
            self.clausulas.extend([ [f"-{var_actual}", var_izq], [f"-{var_actual}", var_der], [var_actual, f"-{var_izq}", f"-{var_der}"] ])
        elif op == 'v':   # x <-> (a v b)
            self.clausulas.extend([ [f"-{var_actual}", var_izq, var_der], [var_actual, f"-{var_izq}"], [var_actual, f"-{var_der}"] ])
        elif op == '->':  # x <-> (a -> b)  ==  x <-> (-a v b)
            self.clausulas.extend([ [f"-{var_actual}", f"-{var_izq}", var_der], [var_actual, var_izq], [var_actual, f"-{var_der}"] ])
        elif op == '<->': # x <-> (a <-> b)
            self.clausulas.extend([ [f"-{var_actual}", f"-{var_izq}", var_der], [f"-{var_actual}", var_izq, f"-{var_der}"], [var_actual, var_izq, var_der], [var_actual, f"-{var_izq}", f"-{var_der}"] ])
        elif op == '-':   # x <-> -a
            self.clausulas.extend([ [f"-{var_actual}", f"-{var_der}"], [var_actual, var_der] ])
        return var_actual

def convertir_a_fnc_tseitin(nodo_raiz: Nodo) -> list:
    """Función principal que aplica la codificación de Tseitin."""
    transformador = TransformadorTseitin()
    variable_raiz = transformador.transformar(nodo_raiz)
    transformador.clausulas.append([variable_raiz])
    return transformador.clausulas

def formato_clausulas(clausulas: list) -> str:
    """Formatea la lista de cláusulas FNC en una cadena legible."""
    return " & ".join([f"({' v '.join(literal for literal in c)})" for c in clausulas])

if __name__ == "__main__":
    expresiones = [
        "(p<->q)->(q->p)", 
        "(p->q)->(-q->-p)", 
        "((p->q)->p)->p"
    ]
    
    for expr in expresiones:
        print(f"===========================================================")
        print(f"Expresión Original: {expr}\n")

        # Se necesita una copia profunda del árbol para cada método
        ast_original = construir_ast_desde_expresion(expr)
        ast_para_clasico = copy.deepcopy(ast_original)
        ast_para_tseitin = copy.deepcopy(ast_original)

        # --- Método Clásico ---
        print("--- Método Clásico (FNC Equivalente) ---")
        fnc_clasica_ast = convertir_a_fnc_clasico(ast_para_clasico)
        fnc_clasica_str = ast_a_cadena(fnc_clasica_ast)
        print(f"Resultado: {fnc_clasica_str}\n")
        
        # --- Método de Tseitin ---
        print("--- Método de Tseitin (FNC Equisatisfacible) ---")
        clausulas_tseitin = convertir_a_fnc_tseitin(ast_para_tseitin)
        print("Cláusulas en formato de lista:")
        print(clausulas_tseitin)
        print("\nCláusulas en formato de expresión:")
        print(formato_clausulas(clausulas_tseitin))
        print(f"===========================================================\n")