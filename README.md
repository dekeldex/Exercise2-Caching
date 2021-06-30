# Exercise2-Caching
Cloud Computing - Exercise 2 - Dekel Binyamin 204845648 | Danielle Guli-Morad 207023029
<br>
<br>
unzip the file
<br>
run the ./deploy.sh
<br>
when the deploy is finnished copy the loadBalancerDns:
<br>
loadBalancerDns:
<br>
my-application-load-balancer-14901734.us-east-2.elb.amazonaws.com
<br>
<br>
you can put as such: curl "http://my-application-load-balancer-14901734.us-east-2.elb.amazonaws.com/put?str_key=BEEF&data=this_is_beef&expiration_date=1234" (or use postman)
<br>
<br>
you can get the data back as such: curl "http://my-application-load-balancer-14901734.us-east-2.elb.amazonaws.com/get?str_key=BEEF" (or use postman)
<br>
<br>
<br>
you can then terminate an instance and then run ./deployNewNode.sh to create a new node and reorganize the data
