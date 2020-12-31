{/*Add elements with D3*/}
<body>
    <script>
        const anchor = d3.select("body").append("h1").text("LearningD3")
    </script>
</body>
{/*Select a group of elements with D3*/}
<body>
    <ul>
        <li>Example</li>
        <li>Example</li>
        <li>Example</li>
    </ul>
    <script>
        const anchor = d3.selectAll("li").text("list item")
    </script>
</body>
{/*Work with Data in D3*/}
<body>
    <script>
        const dataset = [12, 31, 22, 17, 25, 18, 29, 14, 9];
        d3.select("body").selectAll("h2").data(dataset).enter().append("h2").text("New title") 
    </script>
</body>
