; programme
extern printf, atoi
section .data
argv: dq 0
x: dq 0
argc: dd 0
a: dq 0
y: dq 0
returnExpr: db "%d", 10, 0
z: dq 0
b: dq 0

global main
global add
global tripleadd

section .text
; fonction
add:
push rbp
mov rbp, rsp
; initialisation variables fonction
mov rax, [argv]
mov rdi, [rax+8] 
call atoi
mov [x], rax
; initialisation variables fonction
mov rax, [argv]
mov rdi, [rax+16] 
call atoi
mov [y], rax

; return
; operation binaire
; variable
mov rax, [y]

push rax
; variable
mov rax, [x]

pop rbx
add rax, rbx

mov rdi, returnExpr
mov rsi, rax
call printf
pop rbp
ret

; fonction
tripleadd:
push rbp
mov rbp, rsp
; initialisation variables fonction
mov rax, [argv]
mov rdi, [rax+8] 
call atoi
mov [x], rax
; initialisation variables fonction
mov rax, [argv]
mov rdi, [rax+16] 
call atoi
mov [y], rax
; initialisation variables fonction
mov rax, [argv]
mov rdi, [rax+24] 
call atoi
mov [z], rax

; affectation
; appel de fonction
call add

mov [a], rax
; affectation
; appel de fonction
call add

mov [b], rax
; return
; variable
mov rax, [b]

mov rdi, returnExpr
mov rsi, rax
call printf
pop rbp
ret

; fonction main
main:
push rbp
mov [argc], rdi
mov [argv], rsi

mov rax, [argv]
mov rdi, [rax+8]
call atoi
mov [x], rax

mov rax, [argv]
mov rdi, [rax+16]
call atoi
mov [y], rax

mov rax, [argv]
mov rdi, [rax+24]
call atoi
mov [z], rax

; affectation
; appel de fonction
call tripleadd

mov [z], rax
; return
; variable
mov rax, [z]

mov rdi, returnExpr
mov rsi, rax
call printf
pop rbp
ret


