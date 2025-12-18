from client import ApiClient
import time

api1 = ApiClient()
api2 = ApiClient()

api1.login("user1")
api2.login("user2")

api1.send_message("user2", "hello from user1")

ok, msgs = api2.heartbeat()
print(msgs)


print("Register user1")
print(api.register("user1", "", "test_image.png"))

print("Register user2")
print(api.register("user2", "", "test_image.png"))

print("Login user1")
print(api.login("user1"))

print("Login user2")
print(api.login("user2"))

print("Send message user1 -> user2")
print(api.send_message("user2", "hello from user1"))

time.sleep(2)

print("Heartbeat user2")
ok, messages = api.heartbeat()
print(ok, messages)
