import secrets
import math
from typing import Tuple
from config import Config, logger


class PasswordGenerator:
    """
    Motor de generación de contraseñas criptográficamente seguro.
    
    Utiliza el módulo 'secrets' de Python que implementa un CSPRNG
    (Cryptographically Secure Pseudo-Random Number Generator) que lee
    directamente de /dev/urandom (Linux/macOS) o CryptGenRandom (Windows).
    
    RFC 4086 (Randomness Requirements for Security): 
    "Cryptographic random number generators should be used for all
    operations where random numbers are used in cryptographic contexts."
    """
    
    @staticmethod
    def build_alphabet(
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False
    ) -> Tuple[str, int]:
        """
        Construye el alfabeto disponible basado en los parámetros.
        
        Args:
            use_uppercase: Incluir mayúsculas
            use_lowercase: Incluir minúsculas
            use_digits: Incluir dígitos
            use_symbols: Incluir símbolos
            exclude_ambiguous: Excluir caracteres ambiguos (i, l, 1, L, o, 0, O)
        
        Returns:
            Tupla: (alfabeto_str, tamaño_del_alfabeto)
        
        Raises:
            ValueError: Si ningún tipo de carácter está seleccionado
        """
        alphabet = ""
        
        if use_uppercase:
            alphabet += Config.UPPERCASE
        if use_lowercase:
            alphabet += Config.LOWERCASE
        if use_digits:
            alphabet += Config.DIGITS
        if use_symbols:
            alphabet += Config.SYMBOLS
        
        if not alphabet:
            raise ValueError(
                "Al menos un tipo de carácter debe estar seleccionado"
            )
        
        # Excluir caracteres ambiguos si se solicita
        if exclude_ambiguous:
            alphabet = "".join(
                c for c in alphabet if c not in Config.AMBIGUOUS_CHARS
            )
        
        alphabet_size = len(alphabet)
        
        logger.info(
            f"Alfabeto construido: tamaño={alphabet_size}, "
            f"mayus={use_uppercase}, minus={use_lowercase}, "
            f"digs={use_digits}, syms={use_symbols}, "
            f"no_ambi={exclude_ambiguous}"
        )
        
        return alphabet, alphabet_size
    
    @staticmethod
    def generate(
        length: int,
        use_uppercase: bool = True,
        use_lowercase: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
        exclude_ambiguous: bool = False
    ) -> str:
        """
        Genera una contraseña segura utilizando CSPRNG.
        
        Implementación:
        - Construye el alfabeto dinámicamente
        - Para cada posición, usa secrets.choice() para seleccionar
          un carácter aleatorio del alfabeto
        - secrets.choice() utiliza os.urandom() internamente, que es
          la fuente de entropía del SO (nativa, criptográficamente segura)
        
        Returns:
            Contraseña generada como string
        
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        
        # Validación de longitud
        if not isinstance(length, int):
            raise ValueError("length debe ser un entero")
        if length < Config.PASSWORD_MIN_LENGTH or length > Config.PASSWORD_MAX_LENGTH:
            raise ValueError(
                f"length debe estar entre {Config.PASSWORD_MIN_LENGTH} "
                f"y {Config.PASSWORD_MAX_LENGTH}"
            )
        
        # Construir alfabeto
        alphabet, alphabet_size = PasswordGenerator.build_alphabet(
            use_uppercase=use_uppercase,
            use_lowercase=use_lowercase,
            use_digits=use_digits,
            use_symbols=use_symbols,
            exclude_ambiguous=exclude_ambiguous
        )
        
        # Generar contraseña: iteración sobre cada posición
        # secrets.choice() es el CSPRNG que garantiza aleatoriedad criptográfica
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        
        logger.info(
            f"Contraseña generada: longitud={length}, "
            f"alfabeto_size={alphabet_size}"
        )
        
        return password


class PasswordStrengthValidator:
    """
    Validador de fortaleza de contraseña basado en entropía de Shannon.
    
    La entropía es calculada usando la fórmula:
        H = L * log2(N)
    
    donde:
        L = longitud de la contraseña
        N = tamaño del alfabeto utilizado
    
    La entropía en bits indica el número de intentos esperados para
    crackear la contraseña por fuerza bruta. Mientras más alta, más fuerte.
    
    Referencias:
    - NIST SP 800-63B (Digital Identity Guidelines)
    - RFC 4086 (Randomness Requirements for Security)
    """
    
    @staticmethod
    def calculate_entropy(length: int, alphabet_size: int) -> float:
        """
        Calcula la entropía de Shannon en bits.
        
        Formula: H = L * log2(N)
        
        Args:
            length: Longitud de la contraseña
            alphabet_size: Tamaño del alfabeto
        
        Returns:
            Entropía en bits (float)
        """
        if alphabet_size <= 0 or length <= 0:
            return 0.0
        
        entropy = length * math.log2(alphabet_size)
        return round(entropy, 2)
    
    @staticmethod
    def classify_strength(entropy_bits: float) -> str:
        """
        Clasifica la fortaleza de la contraseña según entropía en bits.
        
        Clasificación (basada en NIST SP 800-63B y estándares industriales):
        - very_weak (< 28 bits): Segundos para crackear
        - weak (28-35 bits): Minutos para crackear
        - reasonable (36-59 bits): Horas a días para crackear
        - strong (60-127 bits): Años a siglos para crackear
        - very_strong (>= 128 bits): Infactible con tecnología actual
        
        * Estimación asumiendo 10^12 intentos/segundo (GPU moderna)
        
        Args:
            entropy_bits: Entropía calculada en bits
        
        Returns:
            Clasificación como string
        """
        for strength_level, (min_bits, max_bits) in Config.STRENGTH_THRESHOLDS.items():
            if min_bits <= entropy_bits < max_bits:
                return strength_level
        
        return "very_strong"
    
    @staticmethod
    def validate(
        length: int,
        alphabet_size: int
    ) -> dict:
        """
        Realiza validación completa de una contraseña.
        
        Calcula la entropía de Shannon en bits.
        
        Formula: H = L * log2(N)

        Args:
            length: Longitud de la contraseña
            alphabet_size: Tamaño del alfabeto utilizado
        
        Returns:
            Dict con:
                - entropyBits: Entropía calculada
                - strength: Clasificación de fortaleza
        """
        entropy = PasswordStrengthValidator.calculate_entropy(length, alphabet_size)
        strength = PasswordStrengthValidator.classify_strength(entropy)
        
        logger.info(
            f"Validación completada: longitud={length}, "
            f"alfabeto={alphabet_size}, entropia={entropy} bits, "
            f"strength={strength}"
        )
        
        return {
            "entropyBits": entropy,
            "strength": strength
        }