extern  printf, atoi
        
;hello:  db "Hello world == %d", 10, 0

section .text
global main

section .data
X: dd 0         ; calculé par le compilo
Y: dd 0         ; calculé par le compilo
returnExpr: "%d", 10, 0
argc: dd 0      ; 4 octets
argv: ds 0      ; 8 octets : pointeur

main:   ; le code du compilo
        mov [argc], rdi
        mov [argv], rsi

        ; initialiser les variables
        ; char **argv
        mov rax, [argv] ; rax = argv
        mov rbx, [rax+8] ; rax = argv[1] ou rax = *(argv+8)
        mov rdi, rbx ; rdi = rbx
        call atoi
        mov [X], rax

        ; ... pour la variable Y
        ; initialisation des variables terminée

        ; BODY

        push rbp
        mov rax, 55             ; rax = 55
        cmp rax, 43             ; rax == 43
        je saut
        inc rax                 ; rax++
saut:   mov rdi, returnExpr          ; rdi = returnExpr
        mov rsi, rax            ; rsi = rax
        ;; mov edi, hello
        call printf
        pop rbp
        ret