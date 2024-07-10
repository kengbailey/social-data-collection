<script setup lang="ts">

</script>

<template>
  <main>
    <div class="hometext">
      <p>Home to Social Data Collection fuctionality.</p> 
      <br />
      
      <p>Current functionality:</p>
      <ul>
        <li>- YT Download - Download youtube videos to audio and store locally in s3
          <ul>
            <li>Audio stored as 'best quality' .m4a files</li>
          </ul>
        </li>
      </ul>

      <br /> 
      <p>TODO functionality:</p>
      <ul>
        <li>- YT audio to text</li> 
        <li>- Fetch youtube comments ++ View comments</li>
        <li>- Comment analysis page</li>
      </ul>
    
    </div>

  </main>
</template>

<style>
.hometext {
  padding-top: 20px;
}

li {
  margin-left: 20px; /* Indent each list item */
}
</style>