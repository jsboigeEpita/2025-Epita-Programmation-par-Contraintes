#Copy the dist folder to the nginx image
FROM nginx
# Set the working directory
WORKDIR /usr/share/nginx/html
# Copy the dist folder to the nginx image
COPY /dist /usr/share/nginx/html
# Expose the port the app runs on
EXPOSE 80
# Start nginx
CMD ["nginx", "-g", "daemon off;"]