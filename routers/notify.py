from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from db import async_session
from models import Note, User
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter(tags=["Notify"])


# Store connected clients in a set
# connected_clients = set()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>

        <h2>Your ID: <span id="ws-id"></span></h2>

        <form action="" onsubmit = "sendMessage(event)" >

        <input type="text" id="messageText" autocomplete="off"/>
                    
        <button>Send</button>
   
        </form>

        <ul id='messages'>
        </ul>

        <script>
        var userList = {1,2,3,4,5}
         var client_id = userList.
         
        document.querySelector("#ws-id").textContent = client_id;
        
        var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
        console.log("WebSocket connection established");
                 
        ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };

            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

async def get_id_from_db(name:str):
   
    async with async_session() as async_db:
     try:
        query = select(User).where(User.name == name)
    
        result= await async_db.execute(query)
        # result = await db.execute(query)
        user = result.scalar()
        
        if user is not None:
            print(f"user is {user.id}")
            id = user.id
            user_id = id
            return user_id
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
     except Exception as e:
            print(e)
            await async_db.rollback()


async def is_userid_match_note_owner(user_id, note_id:int):

     async with async_session() as async_db:
        try:
          query = select(Note).where(Note.owner_id == user_id)
    
          result= await async_db.execute(query)
          # result = await db.execute(query)
          user = result.scalar()
        
          if user is not None:
            print(f"user is in 2nd func {user.id}")
            # id = user.id
            # user_id = int(id) # type: ignore
            return True
          raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    
        except Exception as e:
            print(e)
            await async_db.rollback()



class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
  
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)


    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

    async def notify(self, message: str, name:str):

        userid = await get_id_from_db(name)
        print(f"user id in notify is {userid}")
        # work is stopped here, on 14 Dec, 2023. will continue from this, when will have spare time
        
        # need to reengineer these two methods get_id_from_db, is_userid_match_note_owner 
        is_matched = await is_userid_match_note_owner(userid) 
        
        for connection in self.active_connections:
            print(f"is matched is {is_matched}")
            if is_matched is False:
                continue
            await connection.send_text(message)


manager = ConnectionManager()

# @router.get("/")
# async def get():
#     return HTMLResponse(html)


@router.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
    
     await manager.connect(websocket)

     

     try:
       
        while True:
            data = await websocket.receive_text()
            # print(f"Received message from client #{client_id}: {data}")
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            
            await manager.notify(f"Client #{name}: {data}", name=name)
            
     
     except WebSocketDisconnect:
        # print(f"WebSocket connection closed: {client_id}")
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{name} left the chat")

