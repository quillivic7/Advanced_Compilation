main(X, Y) {
while(X) {
   X = X - 1;
   Y = Y + 1;
}
return (Y)
}

main( arg(X, Y), body=() return) 


E ::= V | N | E1 op E2

C ::= V = E | C1 ; C2 | if ( E ) { C } | while( E ) { C } 

P ::= main(liste d'arguments ) { C ; return (E ) ; } 
==============

E  ====> code assembleur qui "calcule" l'expression

section .data
X: dq 0
Y: dq 0
....

E = V
résultat du calcul, on le stocke dans le registre rax
-----------
mov rax, [V] ; récupère le contenu en V et le stocke dans le registre rax

E = N
mov rax, N ; rax = N

E = E1 + E2

//E = (E1 + E2) + E3 ?

compile(E2)
push rax ; stocke la valeur de rax sur la pile ; 
compile(E1)
; dans le haut de la pile, jai la valeur de E2
; et dans rax la valeur de E1


compile(op)  rax, rbx ; add rax, rbx (rax + rbx) : premier argument contient le résulat 
add rax, rbx

====================================

X = E

compile(E) 
mov [X], rax


C1 ; C2

compile(C1)
compile(C2)

if ( E ) { C }

compile(E)
cmp rax, 0
je fin_de_test
compile(C)
fin_de_test : nop

while( E ) { C }

debut_boucle : compile (E) 
cmp rax, 0
je fin_de_boucle
compile(C)
jmp debut_boucle
fin_de_boucle : nop
 






