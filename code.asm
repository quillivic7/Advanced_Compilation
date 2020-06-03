; programme
extern printf, atoi
section .data
returnExpr: db "%d", 10, 0
i: dq 0
argc: dd 0
argv: dq 0
x: dq 0

global main

section .text
; fonction main
main:
push rbp
mov [argc], rdi
mov [argv], rsi

mov rax, [argv]
mov rdi, [rax+8]
call atoi
mov [x], rax

; affectation
; constante
mov rax, 10

mov [i], rax
; while
debut_2:
; variable
mov rax, [i]

cmp rax, 0
jz fin_2
; affectation
; operation binaire
; constante
mov rax, 1

push rax
; variable
mov rax, [x]

pop rbx
add rax, rbx

mov [x], rax
; affectation
; operation binaire
; constante
mov rax, 1

push rax
; variable
mov rax, [i]

pop rbx
sub rax, rbx

mov [i], rax

jmp debut_2
fin_2: nop
; return
; variable
mov rax, [x]

mov rdi, returnExpr
mov rsi, rax
call printf
pop rbp
ret


