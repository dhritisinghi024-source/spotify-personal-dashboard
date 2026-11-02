import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ----------------------------------
# 1. LOAD THE DATA
# ----------------------------------

df = pd.read_csv("spotify_history_personal.csv")

# Support different Spotify data formats

column_changes = {
    "master_metadata_track_name": "track_name",
    "master_metadata_album_artist_name": "artist_name"
}

df = df.rename(columns=column_changes)

if "track_name" not in df.columns:
    df["track_name"] = "Unknown"

if "artist_name" not in df.columns:
    df["artist_name"] = "Unknown"

if "ms_played" not in df.columns:
    df["ms_played"] = 0

if "ts" not in df.columns:
    df["ts"] = pd.NaT

# Check whether the required columns exist
required_columns = ["track_name","artist_name","ms_played","ts"]

# ----------------------------------
# 2. CLEAN THE DATA
# ----------------------------------

df = df.dropna(subset=["track_name", "artist_name"]).copy()

df["ms_played"] = pd.to_numeric(
    df["ms_played"], errors="coerce"
).fillna(0)

df["ts"] = pd.to_datetime(
    df["ts"], errors="coerce", utc=True
)

# ----------------------------------
# 3. ANALYSE THE DATA
# ----------------------------------

total_plays = len(df)

total_minutes = df["ms_played"].sum() / 60000

total_hours = total_minutes / 60

unique_songs = df["track_name"].nunique()

unique_artists = df["artist_name"].nunique()

top_songs = df["track_name"].value_counts().head(5)

top_artists = df["artist_name"].value_counts().head(5)

# Calculate listening time for each year
valid_dates = df.dropna(subset=["ts"]).copy()

# Calculate the number of plays each month
valid_dates["Month"] = valid_dates["ts"].dt.strftime("%Y-%m")

monthly_minutes = (valid_dates.groupby("Month")["ms_played"].sum() / 60000)

# ----------------------------------
# 4. DASHBOARD DESIGN
# ----------------------------------
st.markdown("""
<style>
.stApp {
    background-color: #101010;
    color: white;
}

h1, h2, h3, p, label {
    color: white !important;
}

div.stButton > button {
    background-color: #242424;
    color: white;
    border: 1px solid #1DB954;
    border-radius: 12px;
    min-height: 65px;
    width: 100%;
}

div.stButton > button:hover {
    background-color: #1DB954;
    color: black;
}


/* Dashboard section boxes */
.dashboard-box {
    background-color: #191919;
    border: 1px solid #383838;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 18px;
}

/* Coloured accent borders */
.time-box {
    border-left: 5px solid #1DB954;
}

.plays-box {
    border-left: 5px solid #FF69B4;
}

.songs-box {
    border-left: 5px solid #9B7EDE;
}

.artist-box {
    border-left: 5px solid #FFB347;
}

.top-song-box {
    border-left: 5px solid #FF69B4;
}

.chart-box {
    border-top: 3px solid #1DB954;
}


</style>
""", unsafe_allow_html=True)


# Work out the most-played songs and artists

top_songs = df["track_name"].value_counts().head(5)
top_artists = df["artist_name"].value_counts().head(5)

page = st.session_state.get("page", "Home")


# ----------------------------------
# 5. HOME PAGE
# ----------------------------------

if page == "Home":

    st.title("🎧 SPOTIFY LISTENING DASHBOARD")
    st.write("Your listening habits, visualised.")

    st.write("## YOUR LISTENING SUMMARY")

    st.markdown(
        f"""
        <div class="dashboard-box time-box">
            <h3>🟢 TIME LISTENED</h3>
            <h2>{total_minutes:,.0f} minutes</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("🥧 Explore Listening Time by Month"):
        st.session_state["page"] = "Pie Chart"
        st.rerun()



    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""<div class="dashboard-box plays-box">
            <h3>🩷 TOTAL PLAYS</h3>
            <h2>{total_plays:,}</h2>
            </div>
            """,
            unsafe_allow_html=True)
    with col2:
        st.markdown(
            f"""<div class="dashboard-box songs-box">
            <h3>🟣 UNIQUE SONGS</h3>
            <h2>{unique_songs:,}</h2>
            </div>
            """,
            unsafe_allow_html=True)


    col3, col4 = st.columns(2)

  
    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            f"""
            <div class="dashboard-box artist-box">
                <h3>🟠 TOP ARTIST</h3>
                <h2>{top_artists.index[0] if not top_artists.empty else "No data"}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Explore Top Artists →"):
            st.session_state["page"] = "Artists"
            st.rerun()

    with col4:
        st.markdown(
            f"""
            <div class="dashboard-box top-song-box">
                <h3>💗 TOP SONG</h3>
                <h2>{top_songs.index[0] if not top_songs.empty else "No data"}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Explore Top Songs →"):
            st.session_state["page"] = "Songs"
            st.rerun()


    st.write("## 📈 MONTHLY LISTENING")

    if not monthly_minutes.empty:

        
        fig, ax = plt.subplots()

        # Black graph background
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")

        monthly_minutes.plot(
            kind="line",
            marker="o",
            color="#FF69B4",
            ax=ax)

        # Pink graph line
        ticks = ax.get_xticks()
        ticks = [tick for tick in ticks
                 if 0 <= round(tick) < len(monthly_minutes.index)]

        ax.set_xticks(ticks)

        ax.set_xticklabels([
            pd.to_datetime(
                monthly_minutes.index[round(tick)],
                format="%Y-%m"
                ).strftime("%b")

            for tick in ticks],
                           rotation=60)

        # Green axis titles
        ax.set_xlabel("Month", color="#1DB954")
        ax.set_ylabel("Minutes Listened", color="#1DB954")
        ax.set_title("Listening Time by Month", color="#1DB954")

        # Green axis lines and tick marks
        ax.tick_params(axis="both", colors="#1DB954")

        for spine in ax.spines.values():
            spine.set_color("#1DB954")

        ax.tick_params(axis="x", labelrotation=60)
        fig.tight_layout()

        st.pyplot(fig)
        plt.close(fig)

    else:
        st.write("No valid listening dates are available.")



# ----------------------------------
# 6. TOP ARTISTS PAGE
# ----------------------------------

elif page == "Artists":

    st.title("🟠 TOP ARTISTS")
    st.write("Your five most-played artists.")

    if not top_artists.empty:

        for rank, (artist, plays) in enumerate(
            top_artists.items(), start=1
        ):
            col1, col2, col3 = st.columns([1, 5, 2])

            with col1:
                st.markdown(
                    f"<h2 style='color:white;'>#{rank}</h2>",
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"<p style='color: #FFAD70 !important; "
                    f"-webkit-text-fill-color: #FFAD70; "
                    f"font-size: 24px; font-weight: bold;'>"
                    f"{artist}</p>",
                    unsafe_allow_html=True)

            with col3:
                st.markdown(
                    f"<p style='color: #FFAD70 !important; "
                    f"-webkit-text-fill-color: #FFAD70; "
                    f"font-size: 21px; font-weight: bold;'>"
                    f"{plays:,} plays</p>",
                    unsafe_allow_html=True)
                
            st.divider()

    else:
        st.write("No artist data available.")

    if st.button("← Back to Dashboard"):
        st.session_state["page"] = "Home"
        st.rerun()

# ----------------------------------
# 7. TOP SONGS PAGE
# ----------------------------------

elif page == "Songs":

    st.title("🩷 TOP SONGS")
    st.write("Your five most-played songs.")

    if not top_songs.empty:

        for rank, (song, plays) in enumerate(
            top_songs.items(), start=1
        ):
            col1, col2, col3 = st.columns([1, 5, 2])

            with col1:
                st.markdown(
                    f"<h2 style='color:white;'>#{rank}</h2>",
                    unsafe_allow_html=True
                )

            with col2:
               st.markdown(
                   f"<p style='color: #FF69B4 !important; "
                   f"-webkit-text-fill-color: #FF69B4; "
                   f"font-size: 24px; font-weight: bold;'>"
                   f"{song}</p>",
                   unsafe_allow_html=True)
               
            with col3:
                st.markdown(
                    f"<p style='color: #FF69B4 !important; "
                    f"-webkit-text-fill-color: #FF69B4; "
                    f"font-size: 21px; font-weight: bold;'>"
                    f"{plays:,} plays</p>",
                    unsafe_allow_html=True)

            st.divider()

    else:
        st.write("No song data available.")

    if st.button("← Back to Dashboard"):
        st.session_state["page"] = "Home"
        st.rerun()

# ----------------------------------
# 8. LISTENING TIME PIE CHART
# ----------------------------------

elif page == "Pie Chart":

    st.title("🥧 LISTENING TIME BY MONTH")
    st.write("See how your listening time is divided across months.")

    if not monthly_minutes.empty:

        fig, ax = plt.subplots()

        # Black background
        fig.patch.set_facecolor("black")
        ax.set_facecolor("black")

        # Colourful pie chart
        colours = [
            "#1DB954", "#FF69B4", "#9B7EDE",
            "#FFB347", "#00BFFF", "#FF6347",
            "#FFD700", "#40E0D0", "#DA70D6",
            "#ADFF2F", "#FF1493", "#6495ED"
        ]

        ax.pie(
            monthly_minutes.values,
            labels=[pd.to_datetime(month, format="%Y-%m").strftime("%b")
                    for month in monthly_minutes.index],
            colors=[
                colours[i % len(colours)]
                for i in range(len(monthly_minutes))
            ],
            startangle=90,
            textprops={"color": "white", "fontsize": 8}
        )

        ax.set_title(
            "Listening Time by Month",
            color="#1DB954"
        )

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    else:
        st.write("No valid listening dates are available.")

    if st.button("← Back to Dashboard"):
        st.session_state["page"] = "Home"
        st.rerun()

