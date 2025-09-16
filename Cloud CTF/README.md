
- Challenge details

    ![alt text](/images/image-1.png)


- Check

    ![alt text](/images/image.png)

- Recon

    ![alt text](/images/image-2.png)


    - Check in [springboot api](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html) → `/actuator/health`

    - It's UP

    ![alt text](/images/image-3.png)

    ![alt text](/images/image-4.png)

    - Check endpoint `/mappings`

    ![alt text](/images/image-5.png)

    - Let's checking there APIs

    ![alt text](/images/image-6.png)

    - Check the `/env`

    ![alt text](/images/image-7.png)

    - Find the `BUCKET`'s challenge on: `challenge01-470f711`

    ![alt text](/images/image-8.png)

    - After fuzzing, find the api `/proxy?url=URL`, but it's not work

    ![alt text](/images/image-9.png)

    - Check `/meta-data`

    ![alt text](/images/image-10.png)

    - Adding [this](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html) `X-aws-ec2-metadata-token-ttl-seconds: 21600` on it for get the token

    ![alt text](/images/image-12.png)

    - Now we got the `/lastest/meta-data`. Discovering ...

    ![alt text](/images/image-11.png)

    ![alt text](/images/image-14.png)

    ![alt text](/images/image-13.png)

    - Full `/meta-data/info/`

    ![alt text](/images/image-15.png)

- Config

    ![alt text](/images/image-16.png)

    ![alt text](/images/image-17.png)

- Connect to `s3`

    ![alt text](/images/image-18.png)

    ![alt text](/images/image-19.png)

    ![alt text](/images/image-20.png)

    - Setting the `vpc-endpoint-ids`

    ![alt text](/images/image-21.png)

    ![alt text](/images/image-22.png)

    - Getting the `private/flag.txt` (Local domain)

    ![alt text](/images/image-23.png)

- Read the flag

    ![alt text](/images/image-24.png)
