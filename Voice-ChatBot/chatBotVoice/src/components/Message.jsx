import { useVoice } from "../Context"
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import { faPlay, faStop} from '@fortawesome/free-solid-svg-icons'
import { useState } from "react"
import {Light as SyntaxHighlighter} from 'react-syntax-highlighter';
import { docco } from "react-syntax-highlighter/dist/esm/styles/hljs";

export default function Message({message}) {
    ///////////////////////////////////////////
    const splitMessage = message.body.split('```');  
    const textBeforeCode = splitMessage[0]; // "Lorem ipsum "  
    const codeBlock = splitMessage[1];      // "code block"  
    const textAfterCode = splitMessage[2];  // " text sample"
    console.log(textBeforeCode,"textBeforeCode")
    console.log(codeBlock,"codeBlock")
    console.log(textAfterCode,"textAfterCode")
    ///////////////////////////////////////////
    console.log(message,"poooooo")
    const {play, isPlaying, setIsChatOnGoing, pause} = useVoice()
    const [playc, setPlayc] = useState(false)
    return(
        <li className={message.ownedByCurrentUser ? 'sent' : 'replies'}>
            <div className='bot' style={message.ownedByCurrentUser ? {float: "left"} : {float: "right"}}>
                {message.ownedByCurrentUser ? <img src="/src/images/logo.png" alt="bot" /> : <img src="/src/images/icon.png" alt="user" />}
            </div>
            <div className={message.ownedByCurrentUser ? 'bot-msg' : 'user-msg'}>
                <SyntaxHighlighter language="python" style={docco} >

                </SyntaxHighlighter>
                <span>{message.body}</span>

                <div className="play-icon-bot">
                    {message.isVoice && (
                        <span>
                            <FontAwesomeIcon icon={playc ? faStop : faPlay} onClick={() => {
                                if(!isPlaying){
                                    setIsChatOnGoing(true);
                                    play(message.voice);
                                    setPlayc(true)
                                } else {
                                    pause();
                                    setPlayc(false)
                                }
                            }} />
                        </span>
                    )}
                </div>
            </div>
        </li>
    )
}