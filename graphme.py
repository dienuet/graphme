import sys
import argparse
import requests as rq
import json

builtin_keywords =["Int","String","Boolean","__Schema","__Type","__TypeKind","__Field","__InputValue","__EnumValue","__Directive","__DirectiveLocation"]

def send_request(url,query):
	#proxy = {"http":"http://127.0.0.1:8080"}
	headers = {
		"Authorization":"Bearer xxx",
		"X-CSRF-Token":"vmB7mcl1pOvfF9UYrJoKtnHFXZ8Xkc394hbALadQebtx0j3Y1oWlEGRGV3yqYT0vNzzupk2owpwAiGgFzNYqzg==",
		"Cookie":"_octo=GH1.1.641034266.1581950910; _ga=GA1.2.471217135.1581950912; logged_in=yes; dotcom_user=seehack; _gid=GA1.2.425318925.1591806255; _gat=1; _graphql_explorer_session=c2dwWFBFUCtVV2xUZGxOM3N3bmdHME9ZNm9mclVPTC9rdDUvRDY2OUYyNGtva3FuTHcyNWhDYnZpTjR3UDJnZW9YSG8yQUNHL1dlSHZZUmI4Ykh5TEFxbDgvKzlYYmZoODdheDN0ekpZTjRSQngwUDVKSi9nN0tyUFJ5aGl5NEFvK1FLa2NzcWNNR2hTeGxmUmJmMGdvY1pZZmlOQ2hRS3M3V1JlS0ZNTFlFUVFsWWdxeHJkalJKdmdRTU1pblVHbXJWSzBxdndhSlRaSDg1ZUlGYndyZ3lzMjJIODRJUXdodFl2ak1FWWg2aFE1SGNoZDc1TDRJTWQzREdmVGVzTEFURTQyZEhEZHROQkxDYWtiZGpiRkhlMkNLczFlYlVtNlRER0syYldMZHBnWUZDd0lNbG5oZm5LaHVlUlBQbzhwbFBjbnVEQjIrWlcvVnNuMjVHandKeDEzK3pNQW5YNXNxdUhLbTNmWWpFPS0tYlNYR2tWWDhMdXc5UERvQUtpcDlSdz09--ce12d19daaf5bcf1b384afaed1b359c556816b9c"
	}
	payload = {'query': query}
	req = rq.post(url,json=payload,headers=headers)#proxies=proxy
	if req.status_code == 200:
		return json.loads(req.content)
	else: 
		print "\033[93mStatus Code is not 200\033[0m"
		exit()


def Graph_schema(url):
	print "\033[95mFetching GraphQL Schema\033[0m"
	print
	query = '''\n{\n  __schema {\n    types {\n      name\n    }\n  }\n}'''
	temp = send_request(url,query)
	r = temp["data"]["__schema"]["types"]
	for i in r:
		if i["name"] not in builtin_keywords:
			print "\033[1;31m" + "Type: " + i["name"] + "\033[0m"
			Get_fileds(url,i["name"])

def Get_fileds(url,typename):
	query = '''{__type(name: "''' + typename + '''") {
    name
    fields {
      name
      type {
        name
        kind
        ofType {
          name
          kind
          ofType {
          name
          kind
          ofType {
          name
          kind
        }
        }
        }
      }
      args {
        name
        type {
          name
          kind
          ofType {
            name
            kind
            ofType {
            name
            kind
            ofType {
            name
            kind
          }
          }
          }
        }
      }
    }
  	}
	}'''
	temp = send_request(url,query)
	r = temp["data"]["__type"]["fields"]
	if r == None:
		print "Fields: Null"
		return
	for i in r:
		Field_parser(i)
		



def Field_parser(fields):
	name = fields["name"]
	if fields["args"] == []:
		print name + ": " + Ret_type_parser(fields["type"])
		
	else:
		print name + "("+Args_parser(fields["args"]) + "): " + Ret_type_parser(fields["type"])


def Ret_type_parser(ret_type): #Support: [Obj], Obj, Obj!, [Obj!], [Obj]!, [Obj!]!
	r = ""
	if ret_type["ofType"] == None and ret_type["kind"] != "LIST" and ret_type["kind"] != "NON_NULL":
		r = ret_type["name"]
	else:
		if ret_type["kind"] == "NON_NULL" and ret_type["ofType"]["ofType"] == None:
			r = ret_type["ofType"]["name"] + "!"
		elif ret_type["kind"] == "NON_NULL" and ret_type["ofType"]["ofType"] != None:
			if ret_type["ofType"]["ofType"]["ofType"] == None:
				r = "[" + ret_type["ofType"]["ofType"]["name"] + "]!"
			else:
				r = "[" + ret_type["ofType"]["ofType"]["ofType"]["name"] + "!]!"			

		elif ret_type["kind"] == "LIST" and ret_type["ofType"]["ofType"] == None:
			r = "[" + ret_type["ofType"]["name"] + "]"
		else:
			r = "[" + ret_type["ofType"]["ofType"]["name"] + "!]"
	return r


def Args_parser(args):
	r = ""
	tmp = len(args)
	if len(args) > 1:
		for i in args:
			tmp = tmp - 1
			if i["type"]["ofType"] == None:
				sw = i["name"] + ": " + i["type"]["name"]
				if tmp !=0:
					sw = sw + ", "
			else:
				if i["type"]["kind"] == "LIST" and i["type"]["kind"] != "NON_NULL":
					if i["type"]["ofType"]["ofType"] == None:
						sw = i["name"] + ": " + "[" + i["type"]["ofType"]["name"] + "]"
						if tmp !=0:
							sw = sw + ", "
					else:
						sw = i["name"] + ": " + "[" + i["type"]["ofType"]["ofType"]["name"] + "!]"
						if tmp !=0:
							sw = sw + ", "
				else:
					if i["type"]["ofType"]["ofType"] == None:
						sw = i["name"] + ": " + i["type"]["ofType"]["name"] + "!"
						if tmp !=0:
							sw = sw + ", "
					else:
						sw = i["name"] + ": " + "[" + i["type"]["ofType"]["ofType"]["ofType"]["name"] + "!]!"
						if tmp !=0:
							sw = sw + ", "

			r = r + sw
	else:
		if args[0]["type"]["ofType"] == None:
			sw = args[0]["name"] + ": " + args[0]["type"]["name"]
		else:
			if args[0]["type"]["kind"] == "LIST" and args[0]["type"]["kind"] != "NON_NULL":
				if args[0]["type"]["ofType"]["ofType"] == None:
					sw = args[0]["name"] + ": " + "[" + args[0]["type"]["ofType"]["name"] + "]"
				else:
					sw = args[0]["name"] + ": " + "[" + args[0]["type"]["ofType"]["ofType"]["name"] + "!]"
			else:
				if args[0]["type"]["ofType"]["ofType"] == None:
					sw = args[0]["name"] + ": " + args[0]["type"]["ofType"]["name"] + "!"
				else:
					sw = args[0]["name"] + ": " + "[" + args[0]["type"]["ofType"]["ofType"]["ofType"]["name"] + "!]!"
		r = r + sw
	return r
	


	
if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', help='URL target. Ex: http://target.com/ , Note: config Custom Headers in send_request()',metavar='')

	args = parser.parse_args()
	if(len(sys.argv) <= 1):
		print parser.print_help()
	else:
		Graph_schema(args.u)
		