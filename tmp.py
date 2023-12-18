def equidistant_numbers(num1, num2):
    if num1 > num2:
        num1, num2 = num2, num1

    distance = (num2 - num1) / 4
    result = [num1 + distance * i for i in range(1, 4)]
    return tuple(result)

# Exemple d'utilisation :
resultat = equidistant_numbers(0, 4)
print(resultat)  # Cela devrait afficher (1.0, 2.0, 3.0)
