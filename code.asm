extern printf, atoi 
section .data
returnExpr: db "%d", 10, 0 ; moule
argc: dd 0              ; 4 octets
argv: dq 0  
Y: dq 0
X: dq 0
global main           ; moule
section .text   
main: 
    push rbp
    ; LE CODE DU COMPILO
    mov [argc], rdi
    mov [argv], rsi
    
        mov rax, [argv]
        mov rdi, [rax+8] 
        call atoi ; le resultat est un entier, il est stocké dans rax
        mov [X], rax
        
        mov rax, [argv]
        mov rdi, [rax+16] 
        call atoi ; le resultat est un entier, il est stocké dans rax
        mov [Y], rax
        
    debut_2:
        mov rax, [X]
        
        cmp rax, 0
        jz fin_2
        mov rax, 1
        
        push rax
        mov rax, [X]
        
        pop rbx
        sub rax, rbx
        
        mov [X], rax
        mov rax, 1
        
        push rax
        mov rax, [Y]
        
        pop rbx
        add rax, rbx
        
        mov [Y], rax
        
        jmp debut_2
        fin_2: nop
         
    mov rax, [Y]
        
    mov rdi, returnExpr
    mov rsi, rax
    call printf
    pop rbp
    ret