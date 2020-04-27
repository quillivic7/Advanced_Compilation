extern  printf
        section .data
hello:  db "Hello world == %d", 10, 0

section .text
        global main

main:
        push rbp
        mov rax, 55             ; rax = 55
        cmp rax, 43            ; rax == 43
        je saut
        inc rax                 ; rax++
saut:   mov rdi, hello          ; rdi = hello
        mov rsi, rax            ; rsi = rax
        ;; mov edi, hello
        call printf
        pop rbp
        ret