'''
To distinguish the same type of wx message with different semantics
For example:
    User may scan some qrcode in many scenarios
    These different scenarios will receive the same type of message like:
        {
            type: 'event',
            event: 'scan',
            scene_id: ..custom string..
        }
    To distinguish them, we define the scene_id should be a json string of an object like:
        {
            etype: 1,
            ..other_parameters..
        }
    Then we can distinguish the same kind of wx message with different semantics by etype
    The dispatcher will dispatch the above message to the following function:
        @dispatcher.event.scan.on_etype(etype=1)
        async def func(client, msg):
            ...
'''
class event_type:
    MODULE_SUBSCRIPTION=1

class dispatcher_type:
    EVENT_DISPATCHER=1
    TEXT_DISPATCHER=2