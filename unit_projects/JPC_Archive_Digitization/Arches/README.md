# JPC Archive Digitization

## Osprey to Arches

Script to create HMO records in Arches. 

## Registering OAuth Application

 * Go to `https://[INSTANCE]/o/applications/`
 * Copy the Client ID and Client Secret

Get access_token after providing creds to the auth route:

```python
def auth() -> Auth:
    response = requests.post(
        AUTH_ENDPOINT,
        data={
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": client_id,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    
    data = response.json()
    
    # If OK, get the token
    if response.status_code == 200 and "access_token" in data:
        return Auth(
            access_token=data["access_token"], refresh_token=data["refresh_token"]
        )
    else:
        raise
```

Then, provide token in header of request:

```python
response = requests.put(
    f"{RESOURCES_ENDPOINT}/{GRAPH_ID}/{resource_id}",
    data=json.dumps(json_data),
    params=(("format", "arches-json"), ("indent", 4)),
    headers={"Authorization": f"Bearer {auth.access_token}"},
)
```

### Current Status: Pre-Pilot

The project is in testing phase and the code will change while we test the best approaches and workflows. This currently runs manually, but will be automated at a later date. 

