# Conversor a Forma Normal Conjuntiva (FNC)

- **Autor:** `Juan Carlos Muñoz Trejos`

## 1. Entorno de Desarrollo

Este proyecto fue desarrollado y probado en el siguiente entorno:

- **Sistema Operativo:** `Windows 11`
- **Intérprete:** `Python 3.10.12`

## 2. Instrucciones de Ejecución

Para ejecutar la solución, sigue estos pasos:

1.  **Clona o descarga el repositorio** y asegúrate de tener el archivo `solucion.py` en tu directorio de trabajo.
2.  **Abre una terminal** o línea de comandos en ese directorio.
3.  **Ejecuta el script** usando el intérprete de Python. El script contiene ejemplos predefinidos y se ejecutará directamente:

    ```bash
    python solucion.py
    ```

4.  **Ver los resultados:** La salida se mostrará directamente en la terminal, presentando cada expresión original y sus conversiones a FNC mediante los dos métodos implementados.

## 3. Explicación Detallada de la Solución

Este proyecto implementa un conversor de fórmulas de lógica proposicional a su **Forma Normal Conjuntiva (FNC)**. Una fórmula está en FNC si es una conjunción de cláusulas, donde cada cláusula es una disyunción de literales (variables proposicionales o sus negaciones).

La solución aborda el problema mediante dos enfoques distintos:

1.  **Método Clásico:** Genera una fórmula lógicamente **equivalente** en FNC.
2.  **Transformación de Tseitin:** Genera una fórmula **equisatisfacible** en FNC, que es más eficiente en términos de tamaño.

### 3.1. Estructura del Código

La solución se compone de varias partes clave:

#### a. Árbol de Sintaxis Abstracta (AST)

La expresión lógica de entrada se convierte primero en un **Árbol de Sintaxis Abstracta (AST)**. Esta es una estructura de datos en árbol donde:
-   Los **nodos hoja** son los operandos (variables proposicionales como `p`, `q`).
-   Los **nodos internos** son los operadores lógicos (`-`, `&`, `v`, `->`, `<->`).

La clase `Nodo` representa cada elemento del árbol. La función `construir_ast_desde_expresion` actúa como un *parser* que lee la cadena de entrada y construye el AST, respetando la precedencia de operadores y los paréntesis.

### 3.2. Método 1: Conversión Clásica (FNC Equivalente)

Este método transforma la fórmula aplicando una serie de reglas de equivalencia lógica hasta que la expresión resultante está en FNC. El proceso sigue estos pasos:

1.  **Eliminar Bicondicionales (`<->`):** Se reemplaza cada subfórmula $A \leftrightarrow B$ por su equivalente $(A \rightarrow B) \land (B \rightarrow A)$.
2.  **Eliminar Implicaciones (`->`):** Se reemplaza cada subfórmula $A \rightarrow B$ por su equivalente $\neg A \lor B$.
3.  **Interiorizar Negaciones (`-`):** Se mueven las negaciones hacia adentro, aplicándolas directamente a las variables proposicionales. Esto se logra mediante:
    -   **Ley de Doble Negación:** $\neg(\neg A) \equiv A$.
    -   **Leyes de De Morgan:**
        -   $\neg(A \land B) \equiv \neg A \lor \neg B$
        -   $\neg(A \lor B) \equiv \neg A \land \neg B$
4.  **Distribuir Disyunción (`v`) sobre Conjunción (`&`):** Se aplica la ley distributiva para convertir expresiones de la forma $(A \land B) \lor C$ o $A \lor (B \land C)$ en una FNC.
    -   $A \lor (B \land C) \equiv (A \lor B) \land (A \lor C)$

**Ventaja:** La FNC resultante es lógicamente equivalente a la original.
**Desventaja:** Este método puede causar una **explosión exponencial** en el tamaño de la fórmula, haciéndolo inviable para expresiones complejas.

### 3.3. Método 2: Transformación de Tseitin (FNC Equisatisfacible)

La transformación de Tseitin es un algoritmo mucho más eficiente que convierte una fórmula en FNC en tiempo y espacio lineal. La fórmula resultante no es lógicamente equivalente, pero es **equisatisfacible**, lo que significa que es satisfacible si y solo si la fórmula original lo es. Esto es suficiente para la mayoría de las aplicaciones, como los solucionadores SAT.

El proceso es el siguiente:

1.  **Recorrer el AST:** Se atraviesa el árbol de la fórmula original (generalmente en post-orden).
2.  **Introducir Variables Auxiliares:** Para cada subfórmula representada por un nodo interno (un operador), se introduce una nueva variable auxiliar (ej: $x_1, x_2, \dots$).
3.  **Generar Cláusulas de Definición:** Para cada nueva variable $x_i$, se generan un conjunto de cláusulas que la definen como equivalente a la subfórmula que representa. Por ejemplo, si $x_3$ representa la subfórmula $A \land B$, se generan cláusulas equivalentes a $x_3 \leftrightarrow (A \land B)$. Estas cláusulas ya están en FNC.
    -   Para $x \leftrightarrow (A \land B)$: $(\neg x \lor A) \land (\neg x \lor B) \land (x \lor \neg A \lor \neg B)$
    -   Para $x \leftrightarrow (A \lor B)$: $(\neg x \lor A \lor B) \land (x \lor \neg A) \land (x \lor \neg B)$
    -   Y así sucesivamente para todos los operadores.
4.  **Conjunto Final de Cláusulas:** La FNC final es la conjunción de todas las cláusulas de definición generadas, más una **cláusula unitaria** que contiene la variable que representa la raíz del árbol (la fórmula completa).

**Ventaja:** El tamaño de la FNC resultante es **lineal** con respecto al tamaño de la fórmula original, evitando la explosión exponencial.
**Desventaja:** La FNC no es lógicamente equivalente a la original, solo equisatisfacible.

## 4. Fuentes y Referencias

- Asistente de IA: Gemini fue utilizado como asistente en la generación y depuración del código, así como para aclarar la estructura de los algoritmos y los conceptos teóricos subyacentes.

- Libro: Ben-Ari, M. (2012). Mathematical Logic for Computer Science. Springer.