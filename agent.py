import json
import os
import time
import getpass
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants

def main():
    # --- 1. Cargar Configuración y Clave Secreta ---
    with open("config.json") as f:
        config = json.load(f)

    account_address = config["account_address"]

    # Intentar obtener la clave de la variable de entorno primero
    secret_key = os.environ.get("HYPERLIQUID_SECRET_KEY")

    # Si no está en la variable de entorno, pedirla de forma segura
    if not secret_key:
        try:
            secret_key = getpass.getpass("Introduce tu clave secreta (secret_key): ")
        except (IOError, EOFError):
            print("\nNo se pudo leer la clave. Ejecución cancelada.")
            return

    if not secret_key:
        print("Error: No se ha proporcionado una clave secreta. No se puede continuar.")
        return

    print(f"\nIniciando agente para la cuenta: {account_address}")

    # --- 2. Conectar a la Testnet de Hyperliquid ---
    info = Info(constants.TESTNET_API_URL, skip_ws=True)
    exchange = Exchange(account_address, secret_key, constants.TESTNET_API_URL)

    # --- 3. Definir los Parámetros de la Orden ---
    asset = "BTC"
    is_buy = True
    size_usd = 10  # Tamaño de la orden en USD (una cantidad pequeña para probar)

    # Obtener el precio de mercado actual para calcular el tamaño en la moneda base
    all_mids = info.all_mids()
    market_price = float(all_mids[asset])
    size_asset = size_usd / market_price

    print(f"Intentando colocar una orden de compra de {size_asset:.6f} {asset} (aprox. ${size_usd})...")

    # --- 4. Colocar la Orden ---
    try:
        # El 'slippage' (deslizamiento) se establece en 0.01, que es 1%
        order_result = exchange.order(asset, is_buy, size_asset, None, 0.01)

        if order_result["status"] == "ok":
            status = order_result["response"]["data"]["statuses"][0]
            if "filled" in status:
                print("\n¡Éxito! Orden de mercado ejecutada.")
                print(f"Detalles: {status['filled']}")
            elif "resting" in status:
                 print("\n¡Éxito! Orden límite colocada.")
                 print(f"Detalles: {status['resting']}")
            else:
                print(f"\nOrden enviada, pero estado desconocido: {status}")
        else:
            print(f"\nError al colocar la orden: {order_result}")

    except Exception as e:
        print(f"\n--- Error Inesperado ---")
        print(f"Ocurrió un error al intentar colocar la orden: {e}")
        print("Asegúrate de tener suficientes fondos de la testnet (USDC).")
        print("------------------------\n")

if __name__ == "__main__":
    main()
