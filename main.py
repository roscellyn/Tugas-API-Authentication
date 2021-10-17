import json
from fastapi import FastAPI, HTTPException

with open("menu.json", "r") as read_file:
    data = json.load(read_file)
        
app = FastAPI()
@app.get('/')
def root():
    return{'Menu':'Item'}

@app.get('/menu/{item_id}')
async def read_menu(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            return menu_item
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

@app.get('/menu')
async def read_all_menu():
    return data['menu']
    raise HTTPException(
        status_code=404, detail=f'Data not found'
        )

@app.post('/menu')
async def add_menu(name: str):
    id=1
    if(len(data['menu'])>0):
        id=data['menu'][len(data['menu'])-1]['id']+1
    new_menu = {
        "id": id,
        "name": name
    }
    data['menu'].append(dict(new_menu))
    read_file.close()
    with open("menu.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
    write_file.close()    

    return new_menu
    raise HTTPException(
        status_code=500, detail=f'Internal server error'
        )

@app.put('/menu')
async def update_menu(item_id: int, name: str):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            menu_item['name'] = name
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()

    return({"message": "Menu updated successfully"})
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )

@app.delete('/menu')
async def delete_menu(item_id: int):
    for menu_item in data['menu']:
        if menu_item['id'] == item_id:
            data['menu'].remove(menu_item)
            read_file.close()
            with open("menu.json", "w") as write_file:
                json.dump(data, write_file, indent=4)
            write_file.close()

    return({"message": "Item deleted successfully"})
    raise HTTPException(
        status_code=404, detail=f'Item not found'
        )