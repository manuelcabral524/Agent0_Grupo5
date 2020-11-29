O algoritmo A Star é realizado na função think() da class Agent. Nesta função temos um ciclo while onde basicamente é executado todo o algoritmo.

Antes do ciclo começar temos que identificar qual o nó inicial, daí que o ciclo começa com a variavel 'v' (nó a visitar) a apontar para o nó 'root'.

Ao entrar no ciclo, a primeira coisa que acontece é visitar o nó 'v'. De seguida temos uma condição if/else que serve para verificar-mos se o nó 'v' é o nó de destino. Caso isso seja verdade, o algoritmo termina e o agente faz o percurso que foi calculado. Se o algoritmo ainda não chegou ao nó de destino, vamos analisar os nós fronteira do nó atual.

Segue-se um ciclo for para inserir numa lista auxiliar os nós fronteira por ordem crescente de F cost. No indice 0 dessa lista temos o nó com menor F cost. Neste ciclo for, caso dois nós tenham o mesmo F cost, é colocado primeiro na lista o nó com menor H cost.

De seguida temos outro ciclo for muito simples, no qual vamos guardar os valores que estão na lista auxiliar na lista 'nos_conhecidos'.
Nesta lista são guardados todos os nós conhecidos até ao momento. A lista funciona como uma Priority Queue, ou seja, no início da fila temos os três nós mais recentemente conhecidos por ordem crescente de F cost, seguidos pelos anteriores três nós mais recentemente conhecidos, seguidos por outros três etc.

Finalmente, é escolhido o nó a visitar que é aquele que está no início da Priority Queue. É também atualizado o G cost de modo a que na próxima iteração do algoritmo seja possível calcular adequadamente o F cost de cada nó.    


