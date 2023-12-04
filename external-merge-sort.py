import math
import uuid
import tempfile
import sys
import os

limiter = 'ffffffff-ffff-ffff-ffff-ffffffffffff'

# função responsável por unir duas sublistas em uma (list_ext) de maneira ordenada
def merge(list_ext, i_start_l, i_end_l_start_r, i_end_r):
    qty_left = i_end_l_start_r - i_start_l + 1
    qty_right = i_end_r - i_end_l_start_r
    left = []
    right = []

    # copiando elementos da list principal para as duas sublistas
    for i in range(qty_left):
        left.append(list_ext[i_start_l + i])
    for j in range(qty_right):
        right.append(list_ext[i_end_l_start_r + j + 1])

    left.append(uuid.UUID(limiter))
    right.append(uuid.UUID(limiter))

    i = 0
    j = 0
    for k in range (i_start_l, i_end_r + 1):
        if left[i] <= right[j]:
            list_ext[k] = left[i]
            i += 1
        else: 
            list_ext[k] = right[j]
            j += 1


def merge_sort(list_ext, i_start_l, i_end_r):
    if i_start_l < i_end_r:
        i_end_l_start_r = math.floor((i_start_l + i_end_r)/2)
        merge_sort(list_ext, i_start_l, i_end_l_start_r)
        merge_sort(list_ext, i_end_l_start_r + 1, i_end_r)
        merge(list_ext, i_start_l, i_end_l_start_r, i_end_r)


def sort_and_write(file, list_ext):
    merge_sort(list_ext, 0, len(list_ext) - 1)

    with open(file, 'w') as file:
        for _uuid in list_ext:
            file.writelines(str(_uuid) + "\n")
        file.writelines(limiter)


# MAIN
print("Limite memória (MB):")
size = int(input()) * 500000

print("-- Start --")
# Etapa 1: Distribuição - Criação dos arquivos temporários
print("-- DISTRIBUIÇÃO --\n")
with tempfile.TemporaryDirectory() as temp_dir:
    temp_files = []
    with open('input.txt', 'r') as file: 
        current_block = []
        block_index = 0

        # laço que lê o arquivo gigante
        for line in file:
            # gerando objeto uuid a partir da string lida na linha
            current_block.append(uuid.UUID(line.strip()))

            # se a quantidade de UUIDs armazenada em memória atingir o tamanho fornecido pelo usuário
            if sys.getsizeof(current_block) >= size:
                # guarda o caminho de um novo arquivo temporário
                temp_files.append(os.path.join(temp_dir, 'block_{}.txt'.format(block_index)))
                
                # ordena (em memoria) e escreve o bloco atual no arquivo temporário
                sort_and_write(temp_files[block_index], current_block)
                
                # incrementa o contador para numerar o próximo arquivo temporário
                block_index += 1
                
                # Limpa a lista para armazenar o próximo bloco de UUIDs
                current_block = []

        # se ainda há elementos na lista após o loop, cria um último arquivo temporário
        if len(current_block) > 0:
            temp_files.append(os.path.join(temp_dir, 'block_{}.txt'.format(block_index)))
            sort_and_write(temp_files[block_index], current_block)

    # quantidade de blocos
    n_files = len(temp_files)

    print(n_files, "blocos foram utilizados para ordenar os uuid's.")
    
    # Segunda etapa: Intercalações
    print("-- INTERCALAÇÕES --")
    with open('output.txt', 'w') as output_file:
        smallest_uuids = [0] * n_files
        temp_file_handles = [open(file_path, 'r') for file_path in temp_files]

        # Inicializa os menores UUIDs de cada arquivo temporário
        for i in range(n_files):
            smallest_uuids[i] = uuid.UUID(temp_file_handles[i].readline().strip())

        while True:
            smallest = min(smallest_uuids)

            if str(smallest) == limiter:
                break

            # Escreve o menor UUID no arquivo de saída
            output_file.writelines(str(smallest) + "\n")

            # Atualiza o menor UUID para o próximo da lista correspondente
            for i in range(n_files):
                if smallest == smallest_uuids[i]:
                    smallest_uuids[i] = uuid.UUID(temp_file_handles[i].readline().strip())

    # Fecha os arquivos temporários
    for temp_file_handle in temp_file_handles:
        temp_file_handle.close()

print("Ordenação externa finalizada.")
