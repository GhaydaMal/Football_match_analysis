from sklearn.cluster import KMeans

class TeamAssigner:
    def __init__(self):
        self.team_colors = {} # dictionary stores the colors representing each team
        self.player_team_dict = {} # dictionary maps player IDs to their assigned team
    
    def get_clustering_model(self,image):
        # Reshape the image to 2D array
        image_2d = image.reshape(-1,3)

        # Preform K-means with 2 clusters
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=1) # two clusters (one for the player’s jersey color, one for background)
        kmeans.fit(image_2d) # trained K-Means model

        return kmeans

    def get_player_color(self,frame,bbox):
        image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])] 
        
        # K-means clustering applied to top half of bounding box image to separate the colors into two clusters.
        top_half_image = image[0:int(image.shape[0]/2),:]


        # Get Clustering model > separate the jersey color from other colors  
        kmeans = self.get_clustering_model(top_half_image)

        # Get the cluster labels forr each pixel >> labels tell us which cluster each pixel belongs to.
        labels = kmeans.labels_

        # Reshape the labels to the image shape
        clustered_image = labels.reshape(top_half_image.shape[0],top_half_image.shape[1])

        # Get the player cluster
        corner_clusters = [clustered_image[0,0],clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]]
        # Separating the Background from the Player
        non_player_cluster = max(set(corner_clusters),key=corner_clusters.count)
        player_cluster = 1 - non_player_cluster

        player_color = kmeans.cluster_centers_[player_cluster]

        return player_color

    # determine which jerseys' colors represent the two teams
    def assign_team_color(self,frame, player_detections):
        
        player_colors = []
        for _, player_detection in player_detections.items():
            # retrieves the bbox
            bbox = player_detection["bbox"]
            player_color =  self.get_player_color(frame,bbox)
            player_colors.append(player_color)

        # group the colors into two clusters 
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=10)
        kmeans.fit(player_colors)

        self.kmeans = kmeans

       # assign players to teams
        self.team_colors[1] = kmeans.cluster_centers_[0]
        self.team_colors[2] = kmeans.cluster_centers_[1]


    #figure which team a player belongs to based on color of their jersey
    def get_player_team(self,frame,player_bbox,player_id):
        # check if the player is already assigned
        if player_id in self.player_team_dict:
            return self.player_team_dict[player_id]

        # Get the player's color
        player_color = self.get_player_color(frame,player_bbox)

        team_id = self.kmeans.predict(player_color.reshape(1,-1))[0]
        team_id+=1 # 0=1 , 1=2 for readiblity 

        if player_id ==91:# gooalkeeper 
            team_id=1

        # if this player appears again in frames, the team assignment doesn’t have to be recalculated.
        self.player_team_dict[player_id] = team_id

        return team_id