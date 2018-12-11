module Example {
  sequence<string> SongsList;

  interface Downloader {
    ["amd"] string download(string url);
    SongsList getSongsList();
  };

  interface DownloaderFactory {
    Downloader* make(string name);
  };

  exception RequestCanceledException {};
  enum Status {Pending, InProgress, Done, Error}

  struct ClipData {
    string URL;
    string clipName;
    string endpointIP;
    Status status;
  };

  interface ProgressTopic {
    void notify(ClipData clipData);
  };

  interface SyncTopic {
    void notify(TBD);
  };
};
