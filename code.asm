; PROGRAM
extern printf, atoi

section .data
; VAR_LIST
y: dq 0
returnExpr: db "%d", 10, 0
a: dq 0
x: dq 0
b: dq 0
z: dq 0
argv: dq 0
argc: dd 0

; FUNCTIONS
global main
global add
global tripleadd

section .text
; PROGRAM BODY
; function
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

; affect
; binary opcode
; variable
mov rax, [y]

push rax
; variable
mov rax, [x]

pop rbx
add rax, rbx

mov [a], rax
; return
; variable
mov rax, [a]

mov eax, [a]

;nop
pop rbp
ret
; function
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

; affect
; function call 
call add

mov [a], rax
; affect
; function call 
call add

mov [b], rax
; return
; variable
mov rax, [b]

mov eax, [b]

;nop
pop rbp
ret
; main function
main:
push rbp
mov rbp, rsp
mov [argc], edi
mov [argv], rsi
; main variables init
mov rax, [argv]
mov rdi, [rax+8]
call atoi
mov [x], rax
; main variables init
mov rax, [argv]
mov rdi, [rax+16]
call atoi
mov [y], rax
; main variables init
mov rax, [argv]
mov rdi, [rax+24]
call atoi
mov [z], rax

; affect
; function call 
call tripleadd

mov [z], rax
; return
; variable
mov rax, [z]

mov eax, [z]

mov rdi, returnExpr
mov rsi, rax
call printf
pop rbp
ret

