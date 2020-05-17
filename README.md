# requester
simple web framework

# quick start
```
$ python3 setup.py develop
$ cd example/
$ vim simple_requester.py
urls = [
   <define url you would like to access>
   ]
$ python3 simple_requester.py -c sample.ini
```

# graph
![2020-05-11 18 32 21 app creately com bbafd28c2082](https://user-images.githubusercontent.com/26620426/81546725-c1529580-93b5-11ea-8621-79a335ac639e.png)

## Components
### Schedule
scheduling url request as queue

#### Source
No Input channel, one output channel. Role is to create url request.

#### Sink
No Output channel, one input channel. Role is finlalize url request.
This also can make connect to Source like AkkaStream

### Flow
one input, one output channel. processing url request

#### Fecher
burst requesting urls flow with asyncio

#### Pipeline
processor of request response. it can define process as sync and async.


