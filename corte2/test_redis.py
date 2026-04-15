import redis
import uuid
from redis.exceptions import RedisError


def liberar_lock_seguro(cliente: redis.Redis, lock_key: str, token: str) -> None:
	script = """
	if redis.call('get', KEYS[1]) == ARGV[1] then
		return redis.call('del', KEYS[1])
	else
		return 0
	end
	"""
	cliente.eval(script, 1, lock_key, token)


def demo_lock_distribuido() -> None:
	r = redis.Redis(host="localhost", port=6379, decode_responses=True)
	lock_key = "lock:citas:demo"
	token = str(uuid.uuid4())

	try:
		lock_ok = r.set(lock_key, token, nx=True, ex=5)
		if not lock_ok:
			print("No se pudo tomar el lock. Otro proceso lo tiene.")
			return

		print("Lock adquirido")
		print("TTL actual del lock:", r.ttl(lock_key), "segundos")
	except RedisError as exc:
		print("Error Redis:", exc)
	finally:
		try:
			liberar_lock_seguro(r, lock_key, token)
			print("Lock liberado")
		except RedisError:
			print("No se pudo liberar lock, expirara automaticamente")


if __name__ == "__main__":
	demo_lock_distribuido()